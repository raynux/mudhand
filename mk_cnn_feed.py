import numpy as np
import pandas as pd
import talib
from scipy.stats import zscore

df = pd.read_csv('./feed/orig.csv', index_col='Timestamp', usecols=['Timestamp', 'Open', 'High', 'Low', 'Close'])
# df = df[370000:375000]
# df = df[200000:]
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

print(len(df))
print(st)

# 
# Making X, Y
# 
SEQ_LEN = 60
x_raw1 = np.array([
  zscore(df['closeDiff'].values),
  zscore(df['highDiff'].values),
  zscore(df['lowDiff'].values),
]).transpose()

x_raw2 = np.array([
  zscore(df['bbu5Diff'].values),
  zscore(df['bbu15Diff'].values),
  zscore(df['bbu60Diff'].values),
]).transpose()

x_raw3 = np.array([
  zscore(df['sma5Diff'].values),
  zscore(df['sma15Diff'].values),
  zscore(df['sma60Diff'].values),
]).transpose()

x_raw4 = np.array([
  zscore(df['bbl5Diff'].values),
  zscore(df['bbl15Diff'].values),
  zscore(df['bbl60Diff'].values),
]).transpose()

x_raw5 = np.array([
  df['rsi5'].values,
  df['rsi15'].values,
  df['rsi60'].values,
]).transpose()


x1 = np.zeros((x_raw1.shape[0] - SEQ_LEN, SEQ_LEN, x_raw1.shape[1]), dtype=np.float32)
x2 = np.zeros((x_raw2.shape[0] - SEQ_LEN, SEQ_LEN, x_raw2.shape[1]), dtype=np.float32)
x3 = np.zeros((x_raw3.shape[0] - SEQ_LEN, SEQ_LEN, x_raw3.shape[1]), dtype=np.float32)
x4 = np.zeros((x_raw4.shape[0] - SEQ_LEN, SEQ_LEN, x_raw4.shape[1]), dtype=np.float32)
x5 = np.zeros((x_raw5.shape[0] - SEQ_LEN, SEQ_LEN, x_raw5.shape[1]), dtype=np.float32)


y = np.zeros(x1.shape[0], dtype=np.int8)
for i in range(x1.shape[0]):
  x1[i] = x_raw1[i:i+SEQ_LEN]
  x2[i] = x_raw2[i:i+SEQ_LEN]
  x3[i] = x_raw3[i:i+SEQ_LEN]
  x4[i] = x_raw4[i:i+SEQ_LEN]
  x5[i] = x_raw5[i:i+SEQ_LEN]
  y[i] = futures[i+SEQ_LEN]

print(y.shape)
print(x1.shape)
print(x2.shape)
print(x3.shape)
print(x4.shape)
print(x5.shape)

# Shuffle
p = np.random.permutation(len(y))
y = y[p]
x1 = x1[p]
x2 = x2[p]
x3 = x3[p]
x4 = x4[p]
x5 = x5[p]

np.savez('./feed/cnn/data.npz', x1=x1, x2=x2, x3=x3, x4=x4, x5=x5, y=y)
np.savetxt('./feed/cnn/y.csv', y, fmt='%i', delimiter=',')