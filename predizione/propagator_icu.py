from scipy import stats
import wasp

atoms=[]
myvars = {}
names = {}
reason=[]
threshold = None
icu_values = list()
target_values = list()

# this function is called once
def addedVarName(var, name):
    global atoms, myvars, threshold, names

    names[var] = name
    
    if name.startswith("occurrenceUtility"):
        # occ is the value of the predicate occurrenceUtility
        occ = wasp.getTerms("occurrenceUtility", name)
        atoms.append(var)
        # values of the predicate
        (tid, maxICU, target) = tuple(occ)

        myvars.update({
            var: (int(tid), int(maxICU), float(target.replace('"', ''))),
        })
    

    # Pearson threshold
    if name.startswith("utilityThreshold"):
        threshold_value = wasp.getTerms("utilityThreshold", name)[0].replace('"', '')
        threshold = float(threshold_value)


def getVariablesToFreeze():
    return atoms


def compute(answer_set):
    global threshold, icu_values, target_values

    icu_values = list()
    target_values = list()

    for x in answer_set:
        if x < 0:
            continue
        if x not in myvars:
            continue
        
        (_, maxICU, target) = myvars[x]

        icu_values.append(maxICU)
        target_values.append(target)

    # here we compute the Pearson via scipy library
    pearson_value = stats.pearsonr(icu_values, target_values)[0]
    
    
    # check if computed Pearson value is valid
    # print(threshold, flush=True)
    sat = abs(pearson_value) >= 0.5 #threshold
    return (pearson_value, not sat)


def checkAnswerSet(*answer_set):
    global reason, myvars, names
    reason = []

    answer_set = list(answer_set)
    (pearson, res) = compute(answer_set)

    if res:
        l = [-x for x in myvars if answer_set[x] > 0]
        l.extend([x for x in myvars if answer_set[x] < 0])
        reason.append(l) # il valore di answer_set[x] è negativo se l'atomo è falso
        return wasp.incoherent()

    # we print computed Pearson value and the corresponding answer set
    print(f"Pearson = {pearson} {' '.join([names[x] for x in answer_set if x in names and answer_set[x] > 0])}", flush=True)
    return wasp.coherent()


def getReasonsForCheckFailure():
    global reason
    return wasp.createReasonsForCheckFailure(reason)