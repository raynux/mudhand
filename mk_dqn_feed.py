import numpy as np
import pandas as pd
import talib
from scipy.stats import zscore

df = pd.read_csv('./feed/orig.csv', index_col='Timestamp', usecols=['Timestamp', 'Open', 'High', 'Low', 'Close'])
# df = df[370000:375000]
# df = df[20000:]

df['bbu5'],  df['sma5'],  df['bbl5']  = talib.BBANDS(df['Close'], timeperiod=5)
df['bbu15'], df['sma15'], df['bbl15'] = talib.BBANDS(df['Close'], timeperiod=15)
df['bbu60'], df['sma60'], df['bbl60'] = talib.BBANDS(df['Close'], timeperiod=60)
df['rsi5']  = talib.RSI(df['Close'], timeperiod=5) / 100
df['rsi15'] = talib.RSI(df['Close'], timeperiod=15) / 100
df['rsi60'] = talib.RSI(df['Close'], timeperiod=60) / 100

df['closeDiff'] = df['Close'] / df['Open']
df['highDiff']  = df['Close'] / df['High']
df['lowDiff']   = df['Close'] / df['Low']
df['bbu5Diff']  = df['Close'] / df['bbu5']
df['bbu15Diff'] = df['Close'] / df['bbu15']
df['bbu60Diff'] = df['Close'] / df['bbu60']
df['sma5Diff']  = df['Close'] / df['sma5']
df['sma15Diff'] = df['Close'] / df['sma15']
df['sma60Diff'] = df['Close'] / df['sma60']
df['bbl5Diff']  = df['Close'] / df['bbl5']
df['bbl15Diff'] = df['Close'] / df['bbl15']
df['bbl60Diff'] = df['Close'] / df['bbl60']
df = df[60:]

y = df['Close'].values
np.savetxt('./feed/dqn/y.csv', y, fmt='%0.8f', delimiter=',')
np.savez('./feed/dqn/y.npz', y)

# 
# Making X
# 
x = np.array([
  zscore(df['closeDiff'].values),
  zscore(df['highDiff'].values),
  zscore(df['lowDiff'].values),
  zscore(df['bbu5Diff'].values),
  zscore(df['bbu15Diff'].values),
  zscore(df['bbu60Diff'].values),
  zscore(df['sma5Diff'].values),
  zscore(df['sma15Diff'].values),
  zscore(df['sma60Diff'].values),
  zscore(df['bbl5Diff'].values),
  zscore(df['bbl15Diff'].values),
  zscore(df['bbl60Diff'].values),
  df['rsi5'].values,
  df['rsi15'].values,
  df['rsi60'].values,
])
x = x.transpose()
np.savetxt('./feed/dqn/x.csv', x, fmt='%0.8f', delimiter=',')
np.savez('./feed/dqn/x.npz', x)