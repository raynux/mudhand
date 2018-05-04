import numpy as np
import json
from keras.models import  Model
from keras.layers import Input, Dense, Flatten, Dropout, Conv1D, MaxPooling1D
from keras.layers.merge import concatenate
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping, TensorBoard

EPOCHS=2

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


bids_layer_in = Input(shape=(train_X_bids.shape[1], train_X_bids.shape[2]))
bids_layer = Conv1D(32, 8, strides=1, padding='same', activation='relu')(bids_layer_in)
bids_layer = MaxPooling1D(2, padding='same')(bids_layer)
bids_layer = Dropout(0.5)(bids_layer)
bids_layer = Flatten()(bids_layer)
bids_layer = Dense(units=32, activation='relu')(bids_layer)

asks_layer_in = Input(shape=(train_X_asks.shape[1], train_X_asks.shape[2]))
asks_layer = Conv1D(32, 8, strides=1, padding='same', activation='relu')(asks_layer_in)
asks_layer = MaxPooling1D(2, padding='same')(asks_layer)
asks_layer = Dropout(0.5)(asks_layer)
asks_layer = Flatten()(asks_layer)
asks_layer = Dense(units=32, activation='relu')(asks_layer)

merged = concatenate([bids_layer, asks_layer])
merged = Dropout(0.5)(merged)
merged = Dense(units=16, activation='relu')(merged)

prediction = Dense(units=3, activation='softmax')(merged)

model = Model(inputs=[bids_layer_in, asks_layer_in], outputs=prediction)
model.compile('adam', 'categorical_crossentropy', metrics=['accuracy'])

model.summary()

model.fit([train_X_bids, train_X_asks], train_Y, validation_split=0.3, epochs=EPOCHS, callbacks=[
    EarlyStopping(monitor='val_loss'),
    TensorBoard(log_dir='./logs', histogram_freq=0)
])
merged.save('./model/v1')
