import json
import numpy as np
from keras.models import load_model
from keras.utils import to_categorical

def get_batch_size(fname):
    with open(fname) as f:
        return int(f.readline())

def load_feed(batch_size, fname):
    futures = np.empty((batch_size))
    ladders = np.empty((batch_size, 1000, 2))

    count = 0
    with open(fname) as f:
        line = f.readline()
        while line:
            rec = json.loads(line) 
            futures[count] = rec['future']
            ladders[count] = rec['ladder']
            count += 1
            line = f.readline()
    return (futures, ladders)


print('Loading ....')
batch_size = get_batch_size('./feed/nz_count')
(nz_Y, nz_X) = load_feed(batch_size, './feed/nz')
test_Y = to_categorical(nz_Y, num_classes=3)

model = load_model('./models/model.h5')
results = model.predict(nz_X, verbose=0)

raise_count = 0
drop_count = 0

for result in results.tolist():
    p = np.argmax(result)
    if(p == 1):
        raise_count += 1
    if(p == 2):
        drop_count += 1

print(raise_count)
print(drop_count)