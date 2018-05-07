import json
import datetime
import numpy as np
from keras.models import  Model
from keras.layers import Input, Dense, Flatten, Dropout, Conv1D, MaxPooling1D
from keras.layers.merge import concatenate
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping, TensorBoard

EPOCHS=20

def get_batch_size(fname):
    with open(fname) as f:
        return int(f.readline())

def load_feed(batch_size, fname):
    futures = np.empty((batch_size))
    past = np.empty((batch_size, 60, 4))

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
print(train_Y.shape)
print(train_Y)
train_Y = to_categorical(train_Y, num_classes=3)

print(train_Y.shape)
print(train_X_past.shape)

#
# Building Model
#
past_in = Input(shape=(train_X_past.shape[1], train_X_past.shape[2]))
past = Conv1D(128, 5, strides=1, padding='same', activation='relu')(past_in)
past = MaxPooling1D(2, padding='same')(past)
past = Dropout(0.7)(past)
past = Conv1D(128, 5, strides=1, padding='same', activation='relu')(past)
past = MaxPooling1D(2, padding='same')(past)
past = Dropout(0.7)(past)

past = Flatten()(past)
past = Dense(units=64, activation='relu')(past)
past = Dropout(0.7)(past)
past = Dense(units=64, activation='relu')(past)

# merged = concatenate([bids_layer, asks_layer])
# merged = Dropout(0.5)(merged)
# merged = Dense(units=16, activation='relu')(merged)
# prediction = Dense(units=3, activation='softmax')(merged)
# model = Model(inputs=[bids_layer_in, asks_layer_in], outputs=prediction)

prediction = Dense(units=3, activation='softmax')(past)

model = Model(inputs=past_in, outputs=prediction)
model.compile('adam', 'categorical_crossentropy', metrics=['accuracy'])

# model.summary()

#
# Training
#
model.fit(train_X_past, train_Y, validation_split=0.2, epochs=EPOCHS, callbacks=[
    EarlyStopping(monitor='val_loss', patience=0),
    TensorBoard(log_dir='./logs', histogram_freq=0)
])
model.save(datetime.datetime.now().strftime('./models/%Y%m%d-%H%M.h5'))