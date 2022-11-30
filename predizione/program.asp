usefulItem(K,V) :- item(_, K, V).
{ inCandidatePattern(K,W) } :- usefulItem(K,W).
cardItemset(N) :- #count{ K,W : inCandidatePattern(K,W)} = N.
:- cardItemset(N), maxCardItemset(M), N > M.
:- cardItemset(N), N < 1.
:- inCandidatePattern(K1,V), inCandidatePattern(K2,W), V != W, K1 = K2.
inTransaction(Tid) :- transaction(Tid,_), not incomplete(Tid), not containsNan(Tid).
incomplete(Tid) :- transaction(Tid,_), inCandidatePattern(K,W), not contains(Tid,K,W).
contains(Tid,K,W) :- item(Tid, K, W).
containsNan(Tid) :- transaction(Tid, PatientId), objectUtilityVector(PatientId, 'nan').
containsNan(Tid) :- transaction(Tid, PatientId), transactionUtilityVector(Tid, 'nan').
:- #count{ Tid: inTransaction(Tid) }=N, N < Tho, occurrencesThreshold(Tho).
occurrenceUtility(Tid,MaxICU,Albumin) :- inTransaction(Tid), transaction(Tid, PatientId), objectUtilityVector(PatientId, MaxICU), transactionUtilityVector(Tid, Albumin).
:- #count{ M : occurrenceUtility(T,M,_)} = 1.
:- #count{ M : occurrenceUtility(T,_,M)} = 1.
#show occurrenceUtility/3.
#show inCandidatePattern/2.
