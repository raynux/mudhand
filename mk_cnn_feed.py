import numpy as np
import pandas as pd
import talib
from scipy.stats import zscore

df = pd.read_csv('./feed/orig.csv', index_col='Timestamp', usecols=['Timestamp', 'Open', 'High', 'Low', 'Close'])
# df = df[370000:375000]
df = df[200000:]
# df = df[0:80]

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
df = df[60:] # MAX_TIME_PERIOD



# 
# Making Y
# 
FUTURE_RANGE = 5
THRESHOLD = 0.003

st = {'buy': 0, 'sell': 0}

closes = df['Close'].values
futures = np.ones(len(df), dtype=np.int8)

for i in range(len(df) - FUTURE_RANGE):
  for j in range(1, FUTURE_RANGE):
    diff = (closes[i+j] / closes[i]) - 1
    if diff >= THRESHOLD:
      futures[i] = 0
      st['buy'] += 1
      break
    if diff <= -THRESHOLD:
      futures[i] = 2
      st['sell'] += 1
      break

print(st)

# 
# Making X, Y
# 
SEQ_LEN = 60
x_raw = np.array([
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
x_raw = x_raw.transpose()

x = np.zeros((x_raw.shape[0] - SEQ_LEN, SEQ_LEN, x_raw.shape[1]), dtype=np.float32)
y = np.zeros(x.shape[0], dtype=np.int8)
for i in range(x.shape[0]):
  x[i] = x_raw[i:i+SEQ_LEN]
  y[i] = futures[i+SEQ_LEN]

print(y.shape)
print(x.shape)

# Shuffle
p = np.random.permutation(len(x))
x = x[p]
y = y[p]

np.savez('./feed/cnn/x.npz', x)

np.savetxt('./feed/cnn/y.csv', y, fmt='%i', delimiter=',')
np.savez('./feed/cnn/y.npz', y)