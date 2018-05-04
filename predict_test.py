import json
import numpy as np
from keras.models import load_model

model = load_model("./models/model.h5")

def get_batch_size():
    with open("./feed/count") as f:
        return int(f.readline())

def get_futures(batch_size, fname):
    future = []
    with open(fname) as f:
        line = f.readline()
        while line:
            future.append(int(line))
            line = f.readline()
    return future

def get_price_ladder(batch_size, fname):
    ladder = np.empty((batch_size, 500, 2))
    count = 0
    with open("./feed/future") as f:
        line = f.readline()
        while line:
            ladder[count] = json.loads(line)
            count += 1
            line = f.readline()
    return ladder

batch_size = get_batch_size()
futures = get_futures(batch_size, "./feed/future")
bids = get_price_ladder(batch_size, "./feed/bids")
asks = get_price_ladder(batch_size, "./feed/asks")

print(bids.shape)
print(asks.shape)
print('-------')

result = model.predict([bids, asks], verbose=0)

c = []
for i in range(batch_size):
  predicted = np.argmax(result[i])
  c.append(predicted)
  if(predicted != futures[i]):
    print(i, predicted, futures[i])

# print(c)

# print(np.argmax(result[0]))
# print(result[0].tolist())