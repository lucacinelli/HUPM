from aspars import ASPars
from scipy import stats
from wasabi import msg
import pickle
import json
import os
import subprocess
import signal
from sklearn.linear_model import LinearRegression
import re
import numpy as np

import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

PATTERN_RE = re.compile('inCandidatePattern\((.*?)\)')
PATTERNS_RE_JSON = re.compile('inCandidatePattern\("(.*?)","(.*?)"\)')
OCCURRENCES_RE = re.compile('occurrenceUtility\((\d+),([01]),"(.*?)"\)')

class Runwithinterface:

    def __init__(self):
        self.execute = True
        msg.info("run started")
        self.TARGETS = ['ALBUMIN_MEAN', 'BE_ARTERIAL_MEAN', 'BE_VENOUS_MEAN', 'BIC_ARTERIAL_MEAN', 'BIC_VENOUS_MEAN',
                   'BILLIRUBIN_MEAN', 'BLAST_MEAN',
                   'CALCIUM_MEAN', 'CREATININ_MEAN', 'FFA_MEAN', 'GGT_MEAN', 'GLUCOSE_MEAN', 'HEMATOCRITE_MEAN',
                   'HEMOGLOBIN_MEAN', 'INR_MEAN', 'LACTATE_MEAN',
                   'LEUKOCYTES_MEAN', 'LINFOCITOS_MEAN', 'NEUTROPHILES_MEAN', 'P02_ARTERIAL_MEAN', 'P02_VENOUS_MEAN',
                   'PC02_ARTERIAL_MEAN', 'PC02_VENOUS_MEAN',
                   'PCR_MEAN', 'PH_ARTERIAL_MEAN', 'PH_VENOUS_MEAN', 'PLATELETS_MEAN', 'POTASSIUM_MEAN',
                   'SAT02_ARTERIAL_MEAN', 'SAT02_VENOUS_MEAN', 'SODIUM_MEAN',
                   'TGO_MEAN', 'TGP_MEAN', 'TTPA_MEAN', 'UREA_MEAN', 'DIMER_MEAN', 'BLOODPRESSURE_DIASTOLIC_MEAN',
                   'BLOODPRESSURE_SISTOLIC_MEAN', 'HEART_RATE_MEAN',
                   'RESPIRATORY_RATE_MEAN', 'TEMPERATURE_MEAN', 'OXYGEN_SATURATION_MEAN']

    def get_execute(self):
        return self.execute

    def shellizr(self, arg, terminate=False):
        """Launches a command in a shell, captures stdout and stderr in out."""
        global p
        p = subprocess.Popen(arg, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (out, err) = p.communicate()
        return out.rstrip().decode('utf-8')

    def terminate_process(self):
        #os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        #p.kill()
        self.set_execute(False)
        os.system("pkill -TERM -P %s" % p.pid)

    def parse_time(self, lines):
        """Parserizza il tempo dato dal comando `time`"""
        def parse_single(l):
            (m, s) = l.split('\t')[-1].split('m')
            return (int(m) * float(60)) + float(s[:-1])

        (real_line, user_line, sys_line) = lines
        return (parse_single(real_line), parse_single(user_line), parse_single(sys_line))

    def parse_ans(self, lines, pearson_t):
        """Parserizza l'output di wasp"""
        pearsons = list()
        anss = list()
        out = list()

        with open('cancellare.txt', 'w') as f:
            f.writelines(lines)

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

    def parse_ans_JSON(self, ans, pearson, covered_transactions, intercept, coefficient):
        """Parserizza l'answerset e ritorna un JSON con i valori necessari"""
        patterns = list(map(lambda x: f'{x[1]}={x[2]}', re.finditer(PATTERNS_RE_JSON, ans)))
        return {
            'p': patterns,  # pattern
            'len_p': len(patterns),  # (len) pattern
            't': covered_transactions,  # transazioni coperte
            'len_t': len(covered_transactions),  # (len) transazioni coperte
            'pe': pearson,  # pearson,
            'const': intercept,
            'alfa': coefficient
        }

    def compute_pearson_and_covered_transactions_coefficients(self, ans, feature_name):
        """Calcola la pearson"""
        occurrences = re.findall(OCCURRENCES_RE, ans)
        covered_transactions = list(map(lambda occ: occ[0], occurrences))
        icu = np.fromiter(map(lambda occ: occ[1], occurrences), dtype=float)
        values = np.fromiter(map(lambda occ: occ[2], occurrences), dtype=float)

        # aggiunta del modello tramite il calcolo del LinearRegression
        model = LinearRegression().fit(values.reshape(-1, 1), icu)
        intercept = model.intercept_
        coefficient = model.coef_[0]
        #print("modello di regression ---> ", model)

        #pickle.dump(model, open(f"regression_models/model_{feature_name}.sav", 'wb'))
        ## fine

        return (stats.pearsonr(icu, values)[0], covered_transactions, intercept, coefficient)


    def start(self, target):
        with open('results.csv', 'a') as ifile:
            pearson_t = 0.50
            for max_card_itemset in range(5, 6):
                for occ_t in [5,]:
                    self.update_threshold(occ_t, pearson_t, max_card_itemset)
                    results = self.exe_cmd()

                    # parsing dei risultati e del runtime
                    (pearsons, anss) = self.parse_ans(results[0:-4], pearson_t)
                    (_, run_usr, _) = self.parse_time(results[-3:])

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

                    # ===== LA PARTE PER SALVARE I JSON PER OGNI FEATURES
                    pearson_valid = list()
                    pearson_unvalid = list()

                    # parsing dei risultati e del runtime
                    for ans in results[0:-4]:
                        (pearson, covered_transactions, intercept, coefficient) = self.compute_pearson_and_covered_transactions_coefficients(ans, target)
                        if abs(pearson) >= pearson_t:
                            #print("covered transaction --- > ", covered_transactions)
                            doc = self.parse_ans_JSON(ans, pearson, covered_transactions, intercept, coefficient)

                            # cerca se già non esiste questo pattern o se stesso pattern ma in ordine differente
                            insert = True
                            doc['p'].sort()
                            for pp in pearson_valid:
                                pp['p'].sort()
                                if np.array_equal(pp['p'], doc['p']):
                                    insert = False
                                    break

                            if insert:
                                pearson_valid.append(doc)
                            else:
                                pearson_unvalid.append(doc)
                        else:
                            pearson_unvalid.append(pearson)
                    # parsing del tempo
                    (_, usr_time, sys_time) = self.parse_time(results[-3:])

                    # debug
                    print(f'Results for occ {occ_t}, pearson {pearson_t}, max card itemset {max_card_itemset}: len(ans) {len(pearson_valid)} time (usr) {usr_time} time (sys) {sys_time}')

                    # aggiungo nei results.csv
                    ifile.write(','.join(map(str,
                                             [target, occ_t, pearson_t, max_card_itemset, len(pearson_valid), usr_time,
                                              sys_time])) + '\n')

                    # salvo in un file i risultati
                    with open(f'results/json_{occ_t}_{pearson_t}_{max_card_itemset}/{target}_{occ_t}_{pearson_t}_{max_card_itemset}.json',
                              'w') as ofile:
                        json.dump(pearson_valid, ofile)

                    # ===== LA PARTE PER SALVARE I JSON PER OGNI FEATURES


    def update_threshold(self, occ_t, pearson_t=0.25, max_card_itemset=5):
        body = f'occurrencesThreshold({occ_t}).\nutilityThreshold("{pearson_t}").\nmaxCardItemset({max_card_itemset}).'
        with open('thresholds.edb', 'w') as out_file:
            out_file.write(body)


    def update_threshold_interface(self, occ_t=None, pearson_t=None, max_card_itemset=None):
        body = f'occurrencesThreshold({occ_t}).\nutilityThreshold("{pearson_t}").\nmaxCardItemset({max_card_itemset}).'

        inFile = open('thresholds.edb', 'r')
        outFile = open('temp_thresholds.edb', 'w')
        content = inFile.readlines()
        for line in content:
            if occ_t is not None and 'occurrences' in line:
                outFile.write(f'occurrencesThreshold({occ_t}).\n')
            elif pearson_t is not None and 'utility' in line:
                outFile.write(f'utilityThreshold("{pearson_t}").\n')
            elif max_card_itemset is not None and 'maxCard' in line:
                outFile.write(f'maxCardItemset({max_card_itemset}).')
            else:
                outFile.write(line)

        outFile.flush()
        os.remove('thresholds.edb')
        os.rename('temp_thresholds.edb', 'thresholds.edb')



    def update_target(self, i):
        """Scrivo nel file il predicato di filtraggio del valore che mi interessa"""
        print(f"DA CANCE: update {self.TARGETS}")
        predicate_values = ', '.join(map(lambda idx: 'A' if idx == i else '_', range(len(self.TARGETS))))
        predicate = f'transactionUtilityVector(V, A) :- transactionUtilityVector(V, {predicate_values}).'
        with open('tvu.edb', 'w') as out_file:
            out_file.write(predicate)


    def single_run(self, target):
        """Setup per una run, una run è una serie di esperimenti con un target scelto e
        valori diversi per occurrencesThreshold"""
        msg.info(f"Target is {target}")
        target_idx = self.TARGETS.index(target)
        self.update_target(target_idx)
        self.start(self.TARGETS[target_idx])


    def exe_cmd(self):
        cmd = 'time clingo --mode=gringo --output=smodels prediction.edb tvu.edb thresholds.edb program.asp' + \
            ' | wasp --interpreter=python --plugins-files=propagator_icu -n0 --silent=0'

        lines = self.shellizr(cmd).split('\n')
        return lines

    def set_execute(self, e=True):
        self.execute = e

    def run(self):
        os.system('cp results.csv results.csv.bak')
        os.system('rm results.csv')
        os.system('echo "TARGET,OCCURRENCE_T,UTILITY_T,MAX_ITEMSET,N_ANS,TIME" > results.csv')

        self.set_execute()
        for (i, target) in enumerate(self.TARGETS):
            if self.execute:
                print("target ", target)
                self.single_run(target)
            else:
                break
        self.set_execute(e=False)


    '''
    def fig_maker(self, window):  # this should be called as a thread, then time.sleep() here would not freeze the GUI
        #names = ['group_a', 'group_b', 'group_c']
        np.random.seed(42)
        values = np.random.random(size=int(len(self.TARGETS)/2))
        plt.bar(self.TARGETS[:len(values)], values)
        plt.xlabel('Features', horizontalalignment='right', x=0.1)
        ax = plt.gca()
        ax.tick_params(axis='both', labelrotation=40, labelsize=2)
        plt.tight_layout()

        # plt.scatter(np.random.rand(1,10),np.random.rand(1,10))
        window.write_event_value('-THREAD-', 'done.')
        time.sleep(1)
        fig=plt.gcf()
        fig.set_dpi(300)
        return fig

    def draw_figure(self, canvas, figure, loc=(0, 0)):
        figure_canvas_agg = FigureCanvasTkAgg(figure, master=canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg

    def delete_fig_agg(self, fig_agg):
        fig_agg.get_tk_widget().forget()
        plt.close('all')
    '''