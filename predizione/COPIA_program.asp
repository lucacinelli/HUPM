%% all item values
usefulItem(K,V) :- item(_, K, V).

%% we are interested in only one target, this allows to rewrite transactionUtilityVector easier
%% gia presente nel file tvu.edb in input nel grounder
%transactionUtilityVector(V, A) :- transactionUtilityVector(V, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, A).

%% candidate patterns are generated here
{ inCandidatePattern(K,W) } :- usefulItem(K,W).

%% cardinality of each pattern is at most M
cardItemset(N) :- #count{ K,W : inCandidatePattern(K,W)} = N.
:- cardItemset(N), maxCardItemset(M), N > M.
:- cardItemset(N), N < 1. 

%% no items of the same type in the pattern
:- inCandidatePattern(K1,V), inCandidatePattern(K2,W), V != W, K1 = K2.

%% we consider all the transactions containing the guessed items with the target value different from "nan"
inTransaction(Tid) :- transaction(Tid,_), not incomplete(Tid), not containsNan(Tid).
incomplete(Tid) :- transaction(Tid,_), inCandidatePattern(K,W), not contains(Tid,K,W).
contains(Tid,K,W) :- item(Tid, K, W).
containsNan(Tid) :- transaction(Tid, PatientId), objectUtilityVector(PatientId, "nan").
containsNan(Tid) :- transaction(Tid, PatientId), transactionUtilityVector(Tid, "nan"). 

%% at least Tho transactions
:- #count{ Tid: inTransaction(Tid) }=N, N < Tho, occurrencesThreshold(Tho).

%% the utility of the whole occurrence is the juxstaposition of all the required values
occurrenceUtility(Tid,MaxICU,Albumin) :- inTransaction(Tid), transaction(Tid, PatientId),
    objectUtilityVector(PatientId, MaxICU), transactionUtilityVector(Tid, Albumin).

%% values of the occurrence utility must not be constant, otherwise Pearson is not defined
:- #count{ M : occurrenceUtility(T,M,_)} = 1.
:- #count{ M : occurrenceUtility(T,_,M)} = 1.

%#show utilityThreshold/1.
#show occurrenceUtility/3.
#show inCandidatePattern/2.
%#show usefulItem/2.