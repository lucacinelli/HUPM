from collections import defaultdict
from jinja2 import Template, Environment, FileSystemLoader
from sklearn.linear_model import LinearRegression
from wasabi import msg
import json
import numpy as np
import os
import pandas as pd
import random


def open_df():
    columns = 'PATIENT_VISIT_IDENTIFIER;AGE_ABOVE65;AGE_PERCENTIL;GENDER;DISEASE GROUPING 1;DISEASE GROUPING 2;DISEASE GROUPING 3;DISEASE GROUPING 4;DISEASE GROUPING 5;DISEASE GROUPING 6;HTN;IMMUNOCOMPROMISED;OTHER;ALBUMIN_MEAN;BE_ARTERIAL_MEAN;BE_VENOUS_MEAN;BIC_ARTERIAL_MEAN;BIC_VENOUS_MEAN;BILLIRUBIN_MEAN;BLAST_MEAN;CALCIUM_MEAN;CREATININ_MEAN;FFA_MEAN;GGT_MEAN;GLUCOSE_MEAN;HEMATOCRITE_MEAN;HEMOGLOBIN_MEAN;INR_MEAN;LACTATE_MEAN;LEUKOCYTES_MEAN;LINFOCITOS_MEAN;NEUTROPHILES_MEAN;P02_ARTERIAL_MEAN;P02_VENOUS_MEAN;PC02_ARTERIAL_MEAN;PC02_VENOUS_MEAN;PCR_MEAN;PH_ARTERIAL_MEAN;PH_VENOUS_MEAN;PLATELETS_MEAN;POTASSIUM_MEAN;SAT02_ARTERIAL_MEAN;SAT02_VENOUS_MEAN;SODIUM_MEAN;TGO_MEAN;TGP_MEAN;TTPA_MEAN;UREA_MEAN;DIMER_MEAN;BLOODPRESSURE_DIASTOLIC_MEAN;BLOODPRESSURE_SISTOLIC_MEAN;HEART_RATE_MEAN;RESPIRATORY_RATE_MEAN;TEMPERATURE_MEAN;OXYGEN_SATURATION_MEAN;WINDOW;ICU'
    columns = columns.split(';')
    df = pd.read_excel('Kaggle_Sirio_Libanes_ICU_Prediction.xlsx')
    df = df[columns]
    df['TID'] = range(0, len(df))
    return df


def create_indexes(occ, pearson, maxcard):
    dir_files = f'results_no-propagator/json_{occ}_{pearson}_{maxcard}/'
    json_files = filter(lambda f: f.endswith('.json'), os.listdir(dir_files))

    targets = {}
    # contiene una lista di elementi (p, target) dove p è un pattern che appare in t e target è il target considerato
    t2p = defaultdict(list)

    for json_file in json_files:
        with open(dir_files + json_file) as ifile:
            docs = json.load(ifile)
        # target corrente
        target = json_file.split(f'_{occ}_')[0]
        # in targets ho per ogni target tutti i risultati
        targets[target] = docs
        for doc in docs:
            # pattern in formato str
            p = ' '.join(sorted(doc['p']))
            # aggiungo il pattern all'index transaction
            for t in map(int, doc['t']):
                t2p[t].append((p, target))

    return targets, t2p


def regression_model(input_pattern):
    df = open_df()

    data = list()

    for occ in (10, 15, 20):
        t_pearson, maxcard = 0.5, 5
        msg.info(f"Doing occ = {occ}, pearson = {t_pearson}, maxcard = {maxcard}")
        targets, t2p = create_indexes(occ, t_pearson, maxcard)

        pred_and_actual_values = list()

        # 10 transazioni random
        for k_sample in (10, 20, 50, 100):
            sampled = random.sample(range(df.TID.max() + 1), k_sample)
            print(f"N. random transactions: {k_sample}")

            for random_transaction_index in sampled:
                transaction = df[df.TID == random_transaction_index]

                all_pred = list()

                # estraggo tutti i possibili pattern che stanno in questa transazione
                for (p, target) in t2p[random_transaction_index]:
                    # pattern in formato str
                    pattern = p.split(' ')

                    # per ogni coppia (pattern, target) calcolo: predizione, pearson, n di transazioni in cui appare
                    for doc in targets[target]:
                        if pattern == doc['p']:
                            pearson = abs(doc['pe'])
                            n_trans = doc['len_t']

                            target_values = df.iloc[doc['t']][target].values.reshape(-1, 1)
                            icu_values = df.iloc[doc['t']]['ICU'].values
                            model = LinearRegression().fit(target_values, icu_values)

                            single_pred = np.array(df.iloc[random_transaction_index][target]).reshape(1, -1)
                            y_hat = model.predict(single_pred)

                            all_pred.append([(y_hat, pearson, n_trans), (pearson, n_trans)])

                f_norm = lambda v: 0.0 if v <= 0.5 else 1.0

                if all_pred:
                    final_pred = next(map(f_norm, sum(map(lambda x: x[0][0] * x[0][1] * x[0][2], all_pred)) / sum(
                        map(lambda x: x[1][0] * x[1][1], all_pred))))
                    pred_and_actual_values.append(
                        (random_transaction_index, final_pred, float(transaction.ICU.values[0])))

            n_trans_no_patterns = k_sample - len(pred_and_actual_values)
            precision = len(list(filter(lambda v: v[1] == v[2], pred_and_actual_values))) / float(
                len(pred_and_actual_values))
            print(pred_and_actual_values, precision)

            data.append((occ, t_pearson, maxcard, k_sample, n_trans_no_patterns, precision))

    # jinja environment
    env = Environment(loader=FileSystemLoader('template'))
    template = env.get_template('_predizione.html')

    with open(f'webpage/predizione.html', 'w+') as ofile:
        html = template.render(
            title=f"Predizione",
            data=data
        )
        ofile.write(html)

