import numpy as np
import pandas as pd
from sklearn import datasets, linear_model
from sklearn.linear_model import LinearRegression
import statsmodels.api as sma
from scipy import stats

X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
# y = 1 * x_0 + 2 * x_1 + 3
y = np.dot(X, np.array([1, 2])) + 3

reg = LinearRegression().fit(X, y)

print("score ---> ", reg.score(X, y))
print("coef ---> ", reg.coef_)
print("intercept ---> ", reg.intercept_)
print("af estimate: ---> ", np.exp(reg.intercept_))
#print("prediction ---> ", reg.predict(np.array([[3]]).reshape(-1, 1)) )


### PROVA p-value
diabetes_df = datasets.load_diabetes()
print(diabetes_df)
X = diabetes_df.data
y = diabetes_df.target
X2  = sma.add_constant(X)

_1  = sma.OLS(y, X2)
_2  = _1.fit()

print(_2.pvalues)
print(_2.summary())

###### with scikit-learn

lm = LinearRegression()
X=np.array(X[0]).reshape(-1, 1)
print(y)
lm.fit(X,y)
params = np.append(lm.intercept_,lm.coef_)
predictions = lm.predict(X)
new_X = np.append(np.ones((len(X),1)), X, axis=1)
M_S_E = (sum((y-predictions)**2))/(len(new_X)-len(new_X[0]))
v_b = M_S_E*(np.linalg.inv(np.dot(new_X.T,new_X)).diagonal())
s_b = np.sqrt(v_b)
t_b = params/ s_b
p_val =[2*(1-stats.t.cdf(np.abs(i),(len(new_X)-len(new_X[0])))) for i in t_b]
p_val = np.round(p_val,3)
print(p_val)






