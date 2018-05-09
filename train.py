import json
import datetime
import numpy as np
from keras.models import  Model
from keras.layers import Input, Dense, Flatten, Dropout, Conv1D, MaxPooling1D
from keras.layers.merge import concatenate
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping, TensorBoard

EPOCHS=20
PAST_SEQ=10

def get_batch_size(fname):
    with open(fname) as f:
        return int(f.readline())

def load_feed(batch_size, fname):
    futures = np.empty((batch_size))

    ladders = []
    for n in range(0, PAST_SEQ):
        ladders.append(np.empty((batch_size, 1000, 2), dtype='float32'))

    count = 0
    with open(fname) as f:
        line = f.readline()
        while line:
            rec = json.loads(line) 

            for n in range(0, PAST_SEQ):
                ladders[n][count] = rec['ladders'][n]

            futures[count] = rec['future']
            count += 1
            line = f.readline()
    return (futures, ladders)


print('Loading ....')
batch_size = get_batch_size('./feed/count')

(train_Y, train_X) = load_feed(batch_size, './feed/data')
train_Y = to_categorical(train_Y, num_classes=3)

# print(train_Y.shape)
# print(train_X.shape)

#
# Building Model
#
def mkLadderLayer(ladders):
    layer_ins = []
    layers = []
    for n in range(0, PAST_SEQ):
        layer_in = Input(shape=(ladders[n].shape[1], ladders[n].shape[2]))
        layer = Conv1D(32, 8, strides=1, padding='same', activation='relu')(layer_in)
        layer = MaxPooling1D(2, padding='same')(layer)
        layer = Dropout(0.3)(layer)
        layer = Conv1D(32, 8, strides=1, padding='same', activation='relu')(layer)
        layer = MaxPooling1D(2, padding='same')(layer)
        layer = Dropout(0.3)(layer)
        layer = Flatten()(layer)
        layer = Dense(units=32, activation='relu')(layer)

        layer_ins.append(layer_in)
        layers.append(layer)
    return (layer_ins, layers)

(layer_ins, layers) = mkLadderLayer(train_X)

merged = concatenate(layers)
merged = Dense(units=64, activation='relu')(merged)
merged = Dropout(0.5)(merged)
merged = Dense(units=16, activation='relu')(merged)
output_layer = Dense(units=3, activation='softmax')(merged)

# model = Model(inputs=tuple(layer_ins), outputs=output_layer)
model = Model(inputs=layer_ins, outputs=output_layer)
model.compile('adam', 'categorical_crossentropy', metrics=['accuracy'])

# model.summary()

#
# Training
#
# model.fit(train_X, train_Y, validation_split=0.3, epochs=EPOCHS, callbacks=[
#     EarlyStopping(monitor='val_loss', patience=1),
#     TensorBoard(log_dir='./logs', histogram_freq=0)
# )
model.fit(train_X, train_Y, validation_split=0.3, epochs=EPOCHS, callbacks=[
    EarlyStopping(monitor='val_loss', patience=1),
])
model.save(datetime.datetime.now().strftime('./models/%Y%m%d-%H%M.h5'))
