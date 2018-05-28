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
df = df[60:] # MAX_TIME_PERIOD

# 
# Making Y
# 
FUTURE_RANGE = 180
THRESHOLD = 0.01

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

st['total'] = len(df)
st['ratio'] = (st['buy'] + st['sell']) / st['total']
print(st)

# 
# Making X, Y
# 
SEQ_LEN = 60
x_raw = np.array([
  zscore(df['Close'].values),
  # zscore(df['High'].values),
  # zscore(df['Low'].values),
  # zscore(df['bbu5'].values),
  # zscore(df['bbu15'].values),
  # zscore(df['bbu60'].values),
  # zscore(df['sma5'].values),
  # zscore(df['sma15'].values),
  # zscore(df['sma60'].values),
  # zscore(df['bbl5'].values),
  # zscore(df['bbl15'].values),
  # zscore(df['bbl60'].values),
  df['rsi5'].values,
  df['rsi15'].values,
  df['rsi60'].values,
]).transpose()

x = np.zeros((x_raw.shape[0] - SEQ_LEN, SEQ_LEN, x_raw.shape[1]), dtype=np.float32)


y = np.zeros(x.shape[0], dtype=np.int8)
for i in range(x.shape[0]):
  y[i] = futures[i+SEQ_LEN]
  x[i] = x_raw[i:i+SEQ_LEN]

# Shuffle
p = np.random.permutation(len(y))
y = y[p]
x = x[p]

np.savez('./feed/cnn/data.npz', y=y, x=x)
# np.savetxt('./feed/cnn/y.csv', y, fmt='%i', delimiter=',')