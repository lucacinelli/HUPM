from aspars import ASPars
from wasabi import msg
import json
import os
import subprocess
import re

PATTERN_RE = re.compile('inCandidatePattern\((.*?)\)')

def shellizr(arg):
    """Launches a command in a shell, captures stdout and stderr in out."""
    p = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    (out, err) = p.communicate()
    return out.rstrip().decode('utf-8')


def parse_time(lines):
    """Parserizza il tempo dato dal comando `time`"""
    def parse_single(l):
        (m, s) = l.split('\t')[-1].split('m')
        return (int(m) * float(60)) + float(s[:-1])

    (real_line, user_line, sys_line) = lines
    return (parse_single(real_line), parse_single(user_line), parse_single(sys_line))

def parse_ans(lines, pearson_t):
    """Parserizza l'output di wasp"""
    pearsons = list()
    anss = list()
    out = list()

    # programma non incoherent
    if len(lines) != 1:
        i = 0
        while i < len(lines) - 1:
            # caso in cui ho due pearson di fila, il primo indica un ans vuoto, salta
            if lines[i].startswith('Pearson') and lines[i+1].startswith('Pearson'):
                i = i + 1
                continue

            # aggiunto da LUCA (per evitare il warning PearsonRNearConstantInputWarning: di scipy sulla correlazione)
            if lines[i].startswith("/usr/local/Cellar/"):
                i=i+1
                continue
            
            # parsing pearson e ans
            pearson = float((lines[i].split(' = ')[-1]).split(' ')[0])


            # se pearson è -2.0 oppure non è nella soglia, skip
            if pearson == -2.0 or (pearson > -pearson_t and pearson < pearson_t):
                if pearson != -2.0:
                    out.append(pearson)
                i = i + 2
                continue

            pearsons.append(pearson)
            anss.append(','.join(map(lambda x: x.replace('"', ''), re.findall(PATTERN_RE, lines[i+1]))))

            #anss.append(lines[i+1])
            #ans = ASPars().parse(lines[i+1])
            #anss.append(ans)

            i = i + 2

    msg.fail(f"Min, media, max pearson non valide: {min(pearsons)} {sum(pearsons) / float(len(pearsons))} {max(pearsons)}")
    return (pearsons, anss)
    

TARGETS = ['ALBUMIN_MEAN', 'BE_ARTERIAL_MEAN', 'BE_VENOUS_MEAN', 'BIC_ARTERIAL_MEAN', 'BIC_VENOUS_MEAN', 'BILLIRUBIN_MEAN', 'BLAST_MEAN',
    'CALCIUM_MEAN', 'CREATININ_MEAN', 'FFA_MEAN', 'GGT_MEAN', 'GLUCOSE_MEAN', 'HEMATOCRITE_MEAN', 'HEMOGLOBIN_MEAN', 'INR_MEAN', 'LACTATE_MEAN',
    'LEUKOCYTES_MEAN', 'LINFOCITOS_MEAN', 'NEUTROPHILES_MEAN', 'P02_ARTERIAL_MEAN', 'P02_VENOUS_MEAN', 'PC02_ARTERIAL_MEAN', 'PC02_VENOUS_MEAN',
    'PCR_MEAN', 'PH_ARTERIAL_MEAN', 'PH_VENOUS_MEAN', 'PLATELETS_MEAN', 'POTASSIUM_MEAN', 'SAT02_ARTERIAL_MEAN', 'SAT02_VENOUS_MEAN', 'SODIUM_MEAN',
    'TGO_MEAN', 'TGP_MEAN', 'TTPA_MEAN', 'UREA_MEAN', 'DIMER_MEAN', 'BLOODPRESSURE_DIASTOLIC_MEAN', 'BLOODPRESSURE_SISTOLIC_MEAN', 'HEART_RATE_MEAN',
    'RESPIRATORY_RATE_MEAN', 'TEMPERATURE_MEAN', 'OXYGEN_SATURATION_MEAN']


def start(target):
    with open('results.csv', 'a') as ifile:
        pearson_t = 0.50
        for max_card_itemset in range(5, 6):
            for occ_t in [5,]:
                update_threshold(occ_t, pearson_t, max_card_itemset)
                results = exe_cmd()
                
                # parsing dei risultati e del runtime
                (pearsons, anss) = parse_ans(results[0:-4], pearson_t)
                (_, run_usr, _) = parse_time(results[-3:])
                
                msg.good(f'Results for occ {occ_t}, pearson {pearson_t}, max card itemset {max_card_itemset}: len(ans) {len(anss)}, usr time {run_usr}')

                # scrivo i risultati
                results_filename = f'results/{target}_{occ_t}_{pearson_t}_{max_card_itemset}.txt'
                results_body = map(lambda x: f'{x[0]} -- {x[1]}\n', zip(pearsons, anss))
                with open(results_filename, 'w') as rfile:
                    rfile.writelines(results_body)
                
                #results_filename = f'results/{target}_{occ_t}_{pearson_t}.json'
                #with open(results_filename, 'w') as json_file:
                #    json.dump([pearsons, anss], json_file)

                # aggiungo nei results.csv
                ifile.write(','.join(map(str, [target, occ_t, pearson_t, max_card_itemset, len(pearsons), run_usr])) + '\n')


def update_threshold(occ_t, pearson_t=0.25, max_card_itemset=5):
    body = f'occurrencesThreshold({occ_t}).\nutilityThreshold("{pearson_t}").\nmaxCardItemset({max_card_itemset}).'
    with open('thresholds.edb', 'w') as out_file:
        out_file.write(body)


def update_target(i):
    """Scrivo nel file il predicato di filtraggio del valore che mi interessa"""
    predicate_values = ', '.join(map(lambda idx: 'A' if idx == i else '_', range(len(TARGETS))))
    predicate = f'transactionUtilityVector(V, A) :- transactionUtilityVector(V, {predicate_values}).'
    with open('tvu.edb', 'w') as out_file:
        out_file.write(predicate)


def single_run(target):
    """Setup per una run, una run è una serie di esperimenti con un target scelto e
    valori diversi per occurrencesThreshold"""
    msg.info(f"Target is {target}")
    target_idx = TARGETS.index(target)
    update_target(target_idx)
    start(TARGETS[target_idx])


def exe_cmd():
    cmd = 'time clingo --mode=gringo --output=smodels ../icu_admission_dataset/icu_prediction.edb tvu.edb thresholds.edb ../material_icu_admission/program.asp' + \
        ' | wasp --interpreter=python --plugins-files=propagator_icu -n0 --silent=0'
    
    lines = shellizr(cmd).split('\n')
    return lines


if __name__ == '__main__':
    #os.system('rm results/*')
    os.system('cp results.csv results.csv.bak')
    os.system('rm results.csv')
    os.system('echo "TARGET,OCCURRENCE_T,UTILITY_T,MAX_ITEMSET,N_ANS,TIME" > results.csv')

    for (i, target) in enumerate(TARGETS):
        print("target ", target)
        single_run(target)