import numpy as np
import pandas as pd
import json
from sklearn.tree import DecisionTreeRegressor

# load the options
with open("linux-kernel-size/options.json","r") as f:
    linux_options = json.load(f)

# load csv file by setting options as int8 to save memory

df_train = pd.read_csv("linux-kernel-size/subtrain.csv", dtype={f:np.int8 for f in linux_options}, index_col = 0)

df_test = pd.read_csv("linux-kernel-size/subtest.csv", dtype={f:np.int8 for f in linux_options}, index_col = 0)


# for the train set, X_train is the dataframe of explaining variables...
X_train = df_train[linux_options]

# ... and y_train the variable of interest, the kernel size vmlinux for the training set
y_train = df_train["vmlinux"]

# for the test set, X_test is the dataframe of explaining variables...
X_test = df_test[linux_options]

# Now it is your turn...
# Your goal is to estimate y_test, the kernel size vmlinux for the test set
# Have a good challenge!

dt = DecisionTreeRegressor()

dt.fit(X_train, y_train)

y_pred = dt.predict(X_test)

df = pd.DataFrame([[k for k in X_test.index], y_pred]).transpose()

df.columns = ["Id", "Predicted"]

df.set_index("Id").to_csv("submission.csv")


