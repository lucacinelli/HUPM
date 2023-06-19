from wasabi import msg
import json
import os

def target_prediction(input_pattern, df, df_header, features, item, t_pearson, target_output):
    msg.info("\n====== \nTARGET PREDICTION\n=======\n")
    msg.info(f"Doing with pearson = {t_pearson}")

    target_output = df_header[target_output[0]]
    features_index=dict()
    for f in features:
        features_index.update({df_header[f]: f})

    print("features index: ", features_index)

    # prendere dall'input pattern soltanto le colonne degli ITEM per controllare se sono supportati nei pattern
    T = set()
    for i in item:
        value = input_pattern[i]
        category = df_header[i]
        T.add(f"{category}={value}")

    print("Pattern in input T: ", T)


    # inizializzare le variabili per applicare la formula di predizione finale
    num, den = 0, 0

    try:
        # PASSO 1: per ogni feature f_j (es. IL6, Glucose, etc...)
        dir_files = f'results/'
        json_files = filter(lambda f: f.endswith('.json'), os.listdir(dir_files))
        for json_file in json_files:
            with open(dir_files + json_file) as ifile:
                docs = json.load(ifile)

                f_j_name = json_file.split('.')[0]
                f_j_index = features_index[f_j_name]
                print("actual feature f_j: [", f_j_name, "] con index: ", f_j_index)

                ### PASSO 2: cerca tutti i pattern supportati da  T input
                for doc in docs:
                    p_i = set(doc['p'])
                    #print("T ", T, "\np_i ", p_i)
                    # TODO: prendo indifferentemente i pattern contenuti più piccoli o più grandi rispetto a T
                    if p_i.issuperset(T) or T.issuperset(p_i):
                        c_i_j = float(doc['const'])
                        alfa_i_j = float(doc['alfa'])
                        pearson_i_j = abs(float(doc['pe']))
                        n_transaction_i_j = int(doc['len_t'])
                        pvalue_i_j = float(doc['pvalue'])

                        ### PASSO 3: da (c_i_j e alfa_i_j) ed il valore di x_j di f_j per T calcolo la funzione di regressione
                        ## y_i_j = c_i_j + alfa_i_j * x_j
                        x_j = float(input_pattern[f_j_index])
                        #print("feature ", f_j_name, " la x_j: ", x_j)
                        y_i_j = c_i_j + (alfa_i_j * x_j)

                        ### PASSO 4: salvo i valori intermedi (delle y_i_j) per ogni pattern che supporta T
                        # 1) con la pearson
                        #num = num + (y_i_j * pearson_i_j * n_transaction_i_j)
                        #den = den + (pearson_i_j * n_transaction_i_j)

                        # 2) con il p-value
                        num = num + (y_i_j * (1-pvalue_i_j) * n_transaction_i_j)
                        den = den + ((1-pvalue_i_j) * n_transaction_i_j)

        ### PASSO 5: dopo aver controllato tutti i pattern e calcolato i valori di predizione per  ciascun pattern
        # calcolo la formula finale
        ### Y_FINALE = (SOMMA di y_i_i * p_i_j * n_i_j) / (SOMMA di p_i_j * n_i_j)
        ### Y_FINALE = NUM / DEN
        print("num: ", num)
        print("den: ", den)
        if den!=0:
            Y = num / den
            print("Y prima di round: ", Y)
            Y = round(Y)
            print("Y: ", Y)
            # se negativo generiamo un messaggio di errore
            if Y < 0:
                Y = None
        else:
            Y = None

        return Y

    except Exception as e:
        print("FILE in INPUT NOT FOUND with error e: ", e)
        return "NOT CALCULATED"

