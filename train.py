import numpy as np
import json
from keras.models import Sequential, Model
from keras.layers import Input, Dense, Flatten, Dropout, Conv1D, MaxPooling1D, Merge
from keras.layers.merge import concatenate
from keras.utils import to_categorical

EPOCHS=1

def get_batch_size():
    with open("./feed/count") as f:
        return int(f.readline())

def get_futures(batch_size, fname):
    future = np.empty((batch_size))
    count = 0
    with open(fname) as f:
        line = f.readline()
        while line:
            future[count] = int(line)
            count +=1
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

train_Y = get_futures(batch_size, "./feed/future")
train_Y = to_categorical(train_Y, num_classes=3)

train_X_bids = get_price_ladder(batch_size, "./feed/bids")
train_X_asks = get_price_ladder(batch_size, "./feed/asks")

# train_X = train_X_bids

print(train_Y.shape)
print(train_X_bids.shape)
print(train_X_asks.shape)


# model = Sequential()
# model.add(Conv1D(128, 8, strides=1, padding='same', input_shape=(train_X.shape[1], train_X.shape[2]), activation='relu'))
# model.add(MaxPooling1D(2, padding='same'))
# model.add(Conv1D(64, 8, strides=1, padding='same', activation='relu'))
# model.add(Flatten())
# model.add(Dense(units=32, activation='tanh'))
# model.add(Dense(units=3, activation='softmax'))
# model.compile('adam', 'categorical_crossentropy', metrics=['accuracy'])
# model.summary()

model_bid = Sequential()
model_bid.add(Conv1D(32, 8, strides=1, padding='same', input_shape=(train_X_bids.shape[1], train_X_bids.shape[2]), activation='relu'))
model_bid.add(MaxPooling1D(2, padding='same'))
model_bid.add(Dropout(0.1))
model_bid.add(Conv1D(64, 8, strides=1, padding='same', activation='relu'))
model_bid.add(MaxPooling1D(2, padding='same'))
model_bid.add(Dropout(0.2))
model_bid.add(Flatten())
model_bid.add(Dense(units=64, activation='relu'))

model_ask = Sequential()
model_ask.add(Conv1D(32, 8, strides=1, padding='same', input_shape=(train_X_asks.shape[1], train_X_asks.shape[2]), activation='relu'))
model_ask.add(MaxPooling1D(2, padding='same'))
model_ask.add(Dropout(0.1))
model_ask.add(Conv1D(64, 8, strides=1, padding='same', activation='relu'))
model_ask.add(MaxPooling1D(2, padding='same'))
model_ask.add(Dropout(0.2))
model_ask.add(Flatten())
model_ask.add(Dense(units=64, activation='relu'))

merged = Sequential()
merged.add(Merge([model_bid, model_ask], mode='concat'))
merged.add(Dense(units=64, activation='relu'))
merged.add(Dropout(0.3))
merged.add(Dense(units=32, activation='relu'))
merged.add(Dense(units=3, activation='softmax'))

merged.compile('adam', 'categorical_crossentropy', metrics=['accuracy'])

model_ask.summary()
model_bid.summary()
merged.summary()

merged.fit([train_X_bids, train_X_asks], train_Y, validation_split=0.3, epochs=EPOCHS)
merged.save('./model/v1')
