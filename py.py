import pandas as pd
import numpy as np

df_test = pd.DataFrame(np.random.random(size=(4,4)))
df_test[[1,3]]
print(df_test[[1,3]],'df_test')