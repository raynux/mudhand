import numpy as np
import pandas as pd
import talib
from scipy.stats import zscore
from matplotlib import pyplot

FUTURE_RANGE = 10

df = pd.read_csv('./feed/orig.csv', index_col='Timestamp', usecols=['Timestamp', 'Open', 'High', 'Low', 'Close'])
# df = df[370000:375000]
df = df[20000:]

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

# for idx in df.shape[0] - FUTURE_RANGE:
#   pass


df = df[60:]

y = df['Close'].values
np.savetxt('./feed/y.csv', y, fmt='%0.8f', delimiter=',')
np.savez('./feed/y.npz', y)

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
np.savetxt('./feed/x.csv', x, fmt='%0.8f', delimiter=',')
np.savez('./feed/x.npz', x)


# df['nClose'] = zscore(df['closeDiff'].values)
# df['nHigh']  = zscore(df['highDiff'].values)
# df['nLow']   = zscore(df['lowDiff'].values)
# df['nBbu5']  = zscore(df['bbu5Diff'].values)
# df['nBbu15'] = zscore(df['bbu15Diff'].values)
# df['nBbu60'] = zscore(df['bbu60Diff'].values)
# df['nSma5']  = zscore(df['sma5Diff'].values)
# df['nSma15'] = zscore(df['sma15Diff'].values)
# df['nSma60'] = zscore(df['sma60Diff'].values)
# df['nBbl5']  = zscore(df['bbl5Diff'].values)
# df['nBbl15'] = zscore(df['bbl15Diff'].values)
# df['nBbl60'] = zscore(df['bbl60Diff'].values)

# df.to_csv('./feed/pre.csv')



# pyplot.close()
# pp  = pyplot.plot(df.index, (df['Close']))
# p5u = pyplot.plot(df.index, df['bbu5'], linestyle='dashed')
# p5m = pyplot.plot(df.index, df['sma5'], linestyle='dashed')
# p5l = pyplot.plot(df.index, df['bbl5'], linestyle='dashed')

# p15u = pyplot.plot(df.index, df['bbu15'], linestyle='dashed')
# p15m = pyplot.plot(df.index, df['sma15'], linestyle='dashed')
# p15l = pyplot.plot(df.index, df['bbl15'], linestyle='dashed')

# p60  = pyplot.plot(df.index, df['bbu60'], linestyle='dashed')
# p60m = pyplot.plot(df.index, df['sma60'], linestyle='dashed')
# p60l = pyplot.plot(df.index, df['bbl60'], linestyle='dashed')


# pyplot.legend((pp[0], p5u[0], p5m[0], p5l[0]), ('Price', 'BB UPPER', 'SMA', 'BB LOWER'), loc=2)
# pyplot.grid(True)

# pyplot.show()