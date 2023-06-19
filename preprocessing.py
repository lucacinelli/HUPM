import numpy as np
import pandas as pd
import json
import os
from Pattern import Pattern
from scipy import stats
from sklearn.linear_model import LinearRegression

class Preprocessing:

    def __init__(self):
        self._spmf_input_file = 'spmf_input.txt'
        self._spmf_output_file = 'spmf_output.txt'
        self.json_save_output_folder = 'results/'
        self.json_save_output_file = 'results/{}.json'
        self.word_template = "{}={}"
        self.word_set = set()
        self.dict_idx_word = {}
        self.dict_word_idx = {}
        self.transaction_idx_word = {}
        self._patterns = []


    def preproc_create_words_and_transactions_idx(self, df, df_header, item_list):
        '''
         FASE 1)
            per ogni riga dell'excel: transforma le celle degli item con (nomecolonna:valore)
            queste diventano le "parole" a cui associare indici univoci

         FASE 2)
            trasforma le righe in transazioni di indici (gli indici creati nella  fase precedente riguardo agli item)
         '''

        self.word_set = set()
        self.dict_idx_word = {}
        self.dict_word_idx = {}
        self.transaction_idx_word = {}

        index = 0
        for row_excel in df:
            transaction_ = []
            for item in item_list:
                new_word = self.word_template.format(df_header[item], row_excel[item])
                if new_word not in self.word_set:
                    self.word_set.add(new_word)
                    self.dict_idx_word[index] = new_word
                    self.dict_word_idx[new_word] = index
                    index = index + 1

                transaction_.append(str(self.dict_word_idx[new_word]))

            self.transaction_idx_word[row_excel[0]] = (' '.join(transaction_))


        print(self.word_set)
        print("===========")
        for k in sorted(self.dict_idx_word.keys()):
            print(f'k {k} and v {self.dict_idx_word[k]}')

        print("%%%%%%%%%%%%")

        print("Transaction with index in item col ===> ")
        for k in sorted(self.transaction_idx_word.keys())[:10]:
            print(f'k {k} and v {self.transaction_idx_word[k]}')


    def run_mining(self, threshold, df, df_header, feature_list, target_list, pearson_t):
        '''
            FASE 3)
                applica il freq. pattern miner (con soglia freq. minima)
                output => pattern, supp e l'elenco delle transazioni supportate per ciascun pattern

            FASE 4)
                per ogni pattern e per ogni feature calcolare la pearson (tra feature e target) e correlati (regressione, etcc...)
                Salvare il tutto in un file JSON
        '''

        # FASE 3
        self.write_transactions()
        # FASE 3
        os.system(self._spmf_command(threshold))
        # FASE 3
        self.extract_patterns()
        # FASE 3
        self.extract_transactions_from_patterns()
        # FASE 4
        self.compute_correlation_and_finalizeJSON(df, df_header, feature_list, target_list, pearson_t)

        #print("patterns ==> ", self._patterns[:1])

    def write_transactions(self):
        ''' scrivi le transazioni in un file per SPMF '''

        with open(self._spmf_input_file, 'w') as f:
            for k in sorted(self.transaction_idx_word.keys()):
                f.write(self.transaction_idx_word[k])
                f.write('\n')


    def _spmf_command(self, threshold):
        print(f"java -jar spmf.jar run FPGrowth_itemsets {self._spmf_input_file} " \
               f"{self._spmf_output_file} {threshold}%")
        return f"java -jar spmf.jar run FPGrowth_itemsets {self._spmf_input_file} " \
               f"{self._spmf_output_file} {threshold}%"

    def extract_patterns(self):
        """Extracts the patterns"""
        with open(self._spmf_output_file) as infile:
            self._patterns = list(map(lambda l: Pattern(l.rstrip()), infile))


    def translate_patternItems_into_word(self, pattern):
        for item_idx in pattern.items:
            item_word = self.dict_idx_word[item_idx]
            pattern.items_word.add(item_word)


    def extract_transactions_from_patterns(self):
        """Extracts the transactions supported by each pattern"""

        for k in sorted(self.transaction_idx_word.keys()):
            transaction_items = list(map(int, self.transaction_idx_word[k].split(' ')))
            for pattern in self._patterns:
                if pattern.items.issubset(transaction_items):
                    pattern.transactions.add(k)

                self.translate_patternItems_into_word(pattern)

    def help_dict_pattern_feature(self, feature_list, target):
        pattern_dict = {}
        for feature in feature_list:
            #feature_name = df_header[feature]
            pattern_dict[feature] = list()

        #target_name = df_header[target_list[0]]
        pattern_dict[target] = []

        return pattern_dict

    def compute_regression_and_parametersModel(self, X, Y):

        X = np.array(X).reshape(-1, 1)
        # aggiunta del modello tramite il calcolo del LinearRegression
        model = LinearRegression().fit(X, Y)
        intercept = model.intercept_
        slope = model.coef_[0]
        # print("modello di regression ---> ", model)

        ###### CALCOLO DEL PVALUE ########
        y = np.array(Y)
        params = np.append(model.intercept_, model.coef_)
        predictions = model.predict(X)
        new_X = np.append(np.ones((len(X), 1)), X, axis=1)
        M_S_E = (sum((y - predictions) ** 2)) / (len(new_X) - len(new_X[0]))
        v_b = M_S_E * (np.linalg.inv(np.dot(new_X.T, new_X)).diagonal())
        s_b = np.sqrt(v_b)
        t_b = params / s_b
        p_val = [2 * (1 - stats.t.cdf(np.abs(i), (len(new_X) - len(new_X[0])))) for i in t_b]
        p_val = np.round(p_val, 3)
        pvalue = p_val[1]
        ###### FINE CALCOLO DEL PVALUE ########

        return intercept, slope, pvalue


    def compute_correlation_and_finalizeJSON(self, df, df_header, feature_list, target_list, pearson_t):
        """Assigns to each pattern its correlation"""

        files_json = {}
        for feature in feature_list:
            files_json[feature] = list()


        target = target_list[0]
        for pattern in self._patterns:
            pattern_dict = self.help_dict_pattern_feature(feature_list, target)
            for transaction_idx in pattern.transactions:
                transaction_excel = df.loc[df['ID'] == transaction_idx].values.tolist()[0]

                for feature in feature_list:
                    pattern_dict[feature].append(transaction_excel[feature])

                pattern_dict[target].append(transaction_excel[target])


            '''
            stampe di controllo
            print("====== PATTERN SUCCESSIVO =====")
            print(pattern)
            print("transaction: ")
            print(pattern.transactions)
            print("features: ")
            for feature in feature_list:
                print(pattern_dict[feature])

            print("targes: ")
            print(pattern_dict[target])
            '''

            for feature in feature_list:
                # calcolo Pearson e correlazione
                # considerare soltanto i pattern con un valore di pearson più alto della soglia
                pattern.pearson = stats.pearsonr(np.array(pattern_dict[feature]), np.array(pattern_dict[target]))[0]
                if abs(pattern.pearson) >= pearson_t:
                    #print(f"feature {feature} and pearson {pattern.pearson}")

                    # calcolo correlati (regressione, etc...)
                    a, b, c = self.compute_regression_and_parametersModel(pattern_dict[feature], pattern_dict[target])
                    pattern.intercept = a
                    pattern.slope = b
                    pattern.pvalue = c
                    #print(f"correlation => const {pattern.intercept}, alfa {pattern.slope} and pvalue {pattern.pvalue}")

                    files_json[feature].append(pattern.to_dict())



        '''
        for pattern in self._patterns:
            # index 0 => score, index 1 => sentiment
            values = [(db[tid]['score'], db[tid]['sent']) for tid in pattern.transactions]
            #print(f"VALUES: {values}")
            pattern.correlation = stats.pearsonr(list(map(lambda v: v[0], values)), list(map(lambda v: v[1], values)))[0]
            #TODO: regression https://realpython.com/linear-regression-in-python/
            model = LinearRegression().fit(np.array(list(map(lambda v: v[1], values))).reshape((-1, 1)),
                                           np.array(list(map(lambda v: v[0], values))))
            pattern.slope = model.coef_[0]
        '''

        if not os.path.exists(self.json_save_output_folder):
            # If it doesn't exist, create it
            os.makedirs(self.json_save_output_folder)

        else:
            for f in os.listdir(self.json_save_output_folder):
                print(f)
                os.remove(os.path.join(self.json_save_output_folder, f))


        for feature, to_write in files_json.items():
            feature_name = df_header[feature]
            file_name = self.json_save_output_file.format(feature_name)
            with open(file_name, 'w') as f:
                json.dump(to_write, f)





    #### NON UTILIZZATE
    def preproc_col_into_word(self, df, df_header, item_list):
        '''  transforma le colonne dall'excel (solo gli item) nella stringa => (nomecolonna:valore)
             Quindi genera le WORD dalle colonne item dell'excel
        '''

        self.word_set = set()

        for row_excel in df:
            for item in item_list:
                new_word = self.word_template.format(df_header[item], row_excel[item])
                self.word_set.add(new_word)

        self.generating_idx_to_word()
        self.transaction_to_idx(df, df_header, item_list)

    def generating_idx_to_word(self):
        ''' serve per generare un identificativo univoco per ciascuna word '''

        self.dict_idx_word = {}
        self.dict_word_idx = {}
        index = 0

        for word in self.word_set:
            self.dict_idx_word[index] = word
            self.dict_word_idx[word] = index
            index = index + 1

    def transaction_to_idx(self, df, df_header, item_list):
        ''' trasforma le righe in transazioni di indici '''

        self.transaction_idx_word = {}

        for row_excel in df:
            transaction_ = []
            for item in item_list:
                new_word = self.word_template.format(df_header[item], row_excel[item])
                transaction_.append(str(self.dict_word_idx[new_word]))

            self.transaction_idx_word[row_excel[0]] = (' '.join(transaction_))

        print("Transaction with index in item col ===> ")
        for k in sorted(self.transaction_idx_word.keys())[:10]:
            print(f'k {k} and v {self.transaction_idx_word[k]}')

    #### FINE DI NON UTILIZZATE

    ## VECCHIO METODO input
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