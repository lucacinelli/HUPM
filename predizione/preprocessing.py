import numpy as np
import pandas as pd

class Preprocessing:

    def __init__(self):
        pass

    def input(self, filenamepath):
        ''' TODO Generalizzare l'input parser '''

        # the columns we are interested in and the labels for each item
        columns = 'PATIENT_VISIT_IDENTIFIER;AGE_ABOVE65;AGE_PERCENTIL;GENDER;DISEASE GROUPING 1;DISEASE GROUPING 2;DISEASE GROUPING 3;DISEASE GROUPING 4;DISEASE GROUPING 5;DISEASE GROUPING 6;HTN;IMMUNOCOMPROMISED;OTHER;ALBUMIN_MEAN;BE_ARTERIAL_MEAN;BE_VENOUS_MEAN;BIC_ARTERIAL_MEAN;BIC_VENOUS_MEAN;BILLIRUBIN_MEAN;BLAST_MEAN;CALCIUM_MEAN;CREATININ_MEAN;FFA_MEAN;GGT_MEAN;GLUCOSE_MEAN;HEMATOCRITE_MEAN;HEMOGLOBIN_MEAN;INR_MEAN;LACTATE_MEAN;LEUKOCYTES_MEAN;LINFOCITOS_MEAN;NEUTROPHILES_MEAN;P02_ARTERIAL_MEAN;P02_VENOUS_MEAN;PC02_ARTERIAL_MEAN;PC02_VENOUS_MEAN;PCR_MEAN;PH_ARTERIAL_MEAN;PH_VENOUS_MEAN;PLATELETS_MEAN;POTASSIUM_MEAN;SAT02_ARTERIAL_MEAN;SAT02_VENOUS_MEAN;SODIUM_MEAN;TGO_MEAN;TGP_MEAN;TTPA_MEAN;UREA_MEAN;DIMER_MEAN;BLOODPRESSURE_DIASTOLIC_MEAN;BLOODPRESSURE_SISTOLIC_MEAN;HEART_RATE_MEAN;RESPIRATORY_RATE_MEAN;TEMPERATURE_MEAN;OXYGEN_SATURATION_MEAN;WINDOW;ICU'
        columns = columns.split(';')
        visit_values = columns[13:-2]
        items_values = columns[1:12]
        items_labels = ['above', 'perc', 'gender', *[f'dg{i}' for i in range(1,7)], 'htn', 'immunocompromised']

        # open the dataset (it needs to be in the same directory as this python file)
        df = pd.read_excel(filenamepath)
        df = df[columns]
        df['AGE_PERCENTIL'] = df['AGE_PERCENTIL'].map(lambda ap: 'p90th' if ap == 'Above 90th' else ap)

        # format functions for the predicates
        container = lambda analysis_id: f'container({analysis_id}).'
        obj = lambda patient_id: f'object({patient_id}).'
        transaction = lambda visit_id, patient_id: f'transaction({visit_id}, {patient_id}).'
        item = lambda visit_id, kind_of, value: f'item({visit_id}, "{kind_of}", "{value}").'
        obj_utility = lambda patient_id, max_ICU: f'objectUtilityVector({patient_id},{max_ICU}).'
        transaction_utility = lambda visit_id, values: 'transactionUtilityVector({},{}).'.format(visit_id, ','.join(map(str,values)))

        # processing all the transactions into corresponding predicates
        n = -1
        obj_map, obj_utility_map = dict(), dict()
        transaction_map, transaction_utility_map = dict(), dict()
        items = list()

        for (i, (_, row)) in enumerate(df.iterrows()):
            # max n tuple (consider all if n == -1)
            if i == n:
                break

            patient_id = row.PATIENT_VISIT_IDENTIFIER
            visit_id = i

            if not patient_id in obj_map.keys():
                obj_map[patient_id] = obj(patient_id)
                obj_utility_map[patient_id] = obj_utility(patient_id, df[df.PATIENT_VISIT_IDENTIFIER == patient_id].ICU.max())

            transaction_map[visit_id] = transaction(visit_id, patient_id)
            transaction_utility_map[visit_id] = transaction_utility(visit_id, map(lambda x: f'"{row[x]}"', visit_values))

            for (i, str_value) in zip(range(len(items_labels)), items_labels):
                items.append(item(visit_id, str_value, row[items_values[i]]))

        # write the output file
        with open('prediction.edb', 'w') as out_file:
            out_file.write('\n'.join([
                '%% object(patientId)',
                '%% objectUtilityVector(patientId, maxICU)',
                '%% transaction(visitId, patientId)',
                '%% transactionUtilityVector(visitId, {})'.format(', '.join(visit_values)),
                '%% item(visitId, value) where value is one of ageAbove, agePerc, gender\n\n'
            ]))

            out_file.write(' '.join(obj_map.values()) + '\n')
            out_file.write(' '.join(obj_utility_map.values()) + '\n\n')

            out_file.write(' '.join(transaction_map.values()) + '\n')
            out_file.write(' '.join(transaction_utility_map.values()) + '\n\n')

            out_file.write(' '.join(items) + '\n')