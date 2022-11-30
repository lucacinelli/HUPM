DEFAULT_PROG = "usefulItem(K,V) :- item(_, K, V).\n" \
          "{ inCandidatePattern(K,W) } :- usefulItem(K,W).\n" \
          "cardItemset(N) :- #count{ K,W : inCandidatePattern(K,W)} = N.\n" \
          ":- cardItemset(N), maxCardItemset(M), N > M.\n" \
          ":- cardItemset(N), N < 1.\n" \
          ":- inCandidatePattern(K1,V), inCandidatePattern(K2,W), V != W, K1 = K2.\n" \
          "inTransaction(Tid) :- transaction(Tid,_), not incomplete(Tid), not containsNan(Tid).\n" \
          "incomplete(Tid) :- transaction(Tid,_), inCandidatePattern(K,W), not contains(Tid,K,W).\n" \
          "contains(Tid,K,W) :- item(Tid, K, W).\n" \
          "containsNan(Tid) :- transaction(Tid, PatientId), objectUtilityVector(PatientId, 'nan').\n" \
          "containsNan(Tid) :- transaction(Tid, PatientId), transactionUtilityVector(Tid, 'nan').\n" \
          ":- #count{ Tid: inTransaction(Tid) }=N, N < Tho, occurrencesThreshold(Tho).\n" \
          "occurrenceUtility(Tid,MaxICU,Albumin) :- inTransaction(Tid), transaction(Tid, PatientId), objectUtilityVector(PatientId, MaxICU), transactionUtilityVector(Tid, Albumin).\n" \
          ":- #count{ M : occurrenceUtility(T,M,_)} = 1.\n" \
          ":- #count{ M : occurrenceUtility(T,_,M)} = 1.\n" \
          "#show occurrenceUtility/3.\n" \
          "#show inCandidatePattern/2.\n"

def write_program(prog):
    with open("program.asp", 'w') as f:
        f.write(prog)

def write_edb_fact(tabledata, clustering_list, feature_list, target_list):
    print(f"CALLED {clustering_list}")
    container = lambda analysis_id: f'container({analysis_id}).'
    obj = lambda patient_id: f'object({patient_id}).'
    transaction = lambda visit_id, patient_id: f'transaction({visit_id}, {patient_id}).'
    item = lambda visit_id, kind_of, value: f'item({visit_id}, "{kind_of}", "{value}").'
    obj_utility = lambda patient_id, max_ICU: f'objectUtilityVector({patient_id},{max_ICU}).'
    transaction_utility = lambda visit_id, values: 'transactionUtilityVector({},{}).'.format(visit_id,
                                                                                             ','.join(map(str, values)))


    ### ONLY FOR NAME COLUMNS
    clustering_list_write, clustering_list_write_2, clustering_list_write_3, clustering_map, clustering_utility_map = set(), list(), dict(), list(), dict()
    feature_list_write, feature_map, feature_utility_map = set(), list(), dict()
    target_map = list()

    for c_l in clustering_list:
        clustering_map.append(tabledata[0][c_l])

    for f_l in feature_list:
        feature_map.append(tabledata[0][f_l])

    for t_l in target_list:
        target_map.append(tabledata[0][t_l])

    ### ONLY FOR NAME COLUMNS

    # SCAN CSV TO TAKE VALUE
    for index, c in enumerate(clustering_list):
        for (i, td_row) in enumerate(tabledata):
            if i > 0:
                value_clustering = int(tabledata[i][c])

                # [1] object_utility_vector(99, 1)
                clustering_utility_map[value_clustering] = max(0, int(tabledata[i][target_list[0]]))  # deve essere fatto per più target non solo il primo

                # [2] object(99)
                clustering_list_write.add(value_clustering)

                # [3] transaction(visitID, patientID).
                clustering_list_write_2.append((i-1, value_clustering))

                # [4] transactionUtilityVector(visitID, ALBUMIN, ..., Z)
                tmp_list=list()
                for f in feature_list:
                    tmp_list.append(tabledata[i][f])
                clustering_list_write_3[i-1]=tmp_list
                print(f"ECCOLO {clustering_list_write_3[i-1]}")


    # SCAN TO TRANSLATE IN FACTS and PREDICATES
    with open("prediction.edb", 'w') as f:
        # clustering part
        for i in clustering_list_write:
            f.write(f"object({i}). ") #[2]
        for i in enumerate(clustering_utility_map.values()):
            f.write(f"objectUtilityVector({i[0]},{i[1]}). ") #[1]

        for i in clustering_list_write_2:
            f.write(f"transaction({i[0]}, {i[1]}). ") #[3]

        for i in enumerate(clustering_list_write_3.values()):
            sstring=f"transactionUtilityVector({i[0]}"
            for ii in i[1]:
                sstring+=(f', "{ii}"')
            sstring+=(f").")
            f.write(sstring) #[4]