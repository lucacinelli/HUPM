from numpy.lib.function_base import cov
from aspars import ASPars
from scipy import stats
from wasabi import msg
import json
import numpy as np
import os
import subprocess
import sys
import re


TARGETS = ['ALBUMIN_MEAN', 'BE_ARTERIAL_MEAN', 'BE_VENOUS_MEAN', 'BIC_ARTERIAL_MEAN', 'BIC_VENOUS_MEAN', 'BILLIRUBIN_MEAN', 'BLAST_MEAN',
    'CALCIUM_MEAN', 'CREATININ_MEAN', 'FFA_MEAN', 'GGT_MEAN', 'GLUCOSE_MEAN', 'HEMATOCRITE_MEAN', 'HEMOGLOBIN_MEAN', 'INR_MEAN', 'LACTATE_MEAN',
    'LEUKOCYTES_MEAN', 'LINFOCITOS_MEAN', 'NEUTROPHILES_MEAN', 'P02_ARTERIAL_MEAN', 'P02_VENOUS_MEAN', 'PC02_ARTERIAL_MEAN', 'PC02_VENOUS_MEAN',
    'PCR_MEAN', 'PH_ARTERIAL_MEAN', 'PH_VENOUS_MEAN', 'PLATELETS_MEAN', 'POTASSIUM_MEAN', 'SAT02_ARTERIAL_MEAN', 'SAT02_VENOUS_MEAN', 'SODIUM_MEAN',
    'TGO_MEAN', 'TGP_MEAN', 'TTPA_MEAN', 'UREA_MEAN', 'DIMER_MEAN', 'BLOODPRESSURE_DIASTOLIC_MEAN', 'BLOODPRESSURE_SISTOLIC_MEAN', 'HEART_RATE_MEAN',
    'RESPIRATORY_RATE_MEAN', 'TEMPERATURE_MEAN', 'OXYGEN_SATURATION_MEAN']

PATTERNS_RE = re.compile('inCandidatePattern\("(.*?)","(.*?)"\)')
OCCURRENCES_RE = re.compile('occurrenceUtility\((\d+),([01]),"(.*?)"\)')

MAX_CARD_ITEMSETS_T = [5,]
OCCURRENCES_T = [10, 15, 20]


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


def compute_pearson_and_covered_transactions(ans):
    """Calcola la pearson"""
    occurrences = re.findall(OCCURRENCES_RE, ans)
    covered_transactions = list(map(lambda occ: occ[0], occurrences))
    icu = np.fromiter(map(lambda occ: occ[1], occurrences), dtype=float)
    values = np.fromiter(map(lambda occ: occ[2], occurrences), dtype=float)
    
    return (stats.pearsonr(icu, values)[0], covered_transactions)


def parse_ans(ans, pearson, covered_transactions):
    """Parserizza l'answerset e ritorna un JSON con i valori necessari"""
    patterns = list(map(lambda x: f'{x[1]}={x[2]}', re.finditer(PATTERNS_RE, ans)))
    return {
        'p': patterns,                      # pattern
        'len_p': len(patterns),             # (len) pattern
        't': covered_transactions,          # transazioni coperte
        'len_t': len(covered_transactions), # (len) transazioni coperte
        'pe': pearson,                      # pearson
    }


def start(target):
    with open('results_no-propagator.csv', 'a') as ifile:
        pearson_t = 0.50
        for max_card_itemset in MAX_CARD_ITEMSETS_T:
            for occ_t in OCCURRENCES_T:
                update_threshold(occ_t, pearson_t, max_card_itemset)
                results = exe_cmd()

                pearson_valid = list()
                pearson_unvalid = list()
                
                # parsing dei risultati e del runtime
                for ans in results[0:-4]:
                    (pearson, covered_transactions) = compute_pearson_and_covered_transactions(ans)
                    if abs(pearson) >= pearson_t:
                        doc = parse_ans(ans, pearson, covered_transactions)
                        pearson_valid.append(doc)
                    else:
                        pearson_unvalid.append(pearson)
                # parsing del tempo
                (_, usr_time, sys_time) = parse_time(results[-3:])
                
                # debug
                print(f'Results for occ {occ_t}, pearson {pearson_t}, max card itemset {max_card_itemset}: len(ans) {len(pearson_valid)} time (usr) {usr_time} time (sys) {sys_time}')

                # aggiungo nei results.csv
                ifile.write(','.join(map(str, [target, occ_t, pearson_t, max_card_itemset, len(pearson_valid), usr_time, sys_time])) + '\n')

                # salvo in un file i risultati
                with open(f'results_no-propagator/{target}_{occ_t}_{pearson_t}_{max_card_itemset}.json', 'w') as ofile:
                    json.dump(pearson_valid, ofile)


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
    cmd = 'time clingo --mode=gringo --output=smodels example_libanese_n-all.edb tvu.edb thresholds.edb example_program_libanese_no-prop.asp' + \
        ' | ./wasp/build/release/wasp -n0 --silent=0'
    
    lines = shellizr(cmd).split('\n')
    return lines


if __name__ == '__main__':
    #os.system('rm results_no-propagator/*')
    os.system('cp results_no-propagator.csv results_no-propagator.csv.bak')
    if len(sys.argv) > 1:
        os.system('rm results_no-propagator.csv')
        os.system('echo "TARGET,OCCURRENCE_T,UTILITY_T,MAX_ITEMSET,N_ANS,TIME" > results_no-propagator.csv')

    for (i, target) in enumerate(TARGETS):
        single_run(target)