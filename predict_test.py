import json
import numpy as np
from keras.models import load_model
from keras.utils import to_categorical

model = load_model('./models/model.h5')

def get_batch_size(fname):
    with open(fname) as f:
        return int(f.readline())

def load_feed(batch_size, fname):
    futures = np.empty((batch_size))
    past = np.empty((batch_size, 60, 5))

    count = 0
    with open(fname) as f:
        line = f.readline()
        while line:
            rec = json.loads(line) 
            futures[count] = rec['future']
            past[count] = rec['past']
            count += 1
            line = f.readline()
    return (futures, past)


print('Loading ....')
batch_size = get_batch_size('./feed/count')

(train_Y, train_X_past) = load_feed(batch_size, './feed/data')
train_Y = to_categorical(train_Y, num_classes=3)

result = model.predict(train_X_past, verbose=0)

p = {0: 0, 1: 0, 2: 0}
for i in range(batch_size):
    predicted = np.argmax(result[i])
    p[predicted] += 1

print(p)