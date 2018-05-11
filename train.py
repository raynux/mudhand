import json
import datetime
import numpy as np
from keras.models import  Model
from keras.layers import Input, Dense, Flatten, Dropout, LSTM
from keras.layers.merge import concatenate
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping, TensorBoard

EPOCHS=20
PARAM_NUM=3

def get_num(fname):
    with open(fname) as f:
        return int(f.readline())

def load_feed(batch_size, fname):
    seq_len = get_num('./feed/seq')

    futures = np.empty((batch_size))
    past = np.empty((batch_size, seq_len, 3))

    count = 0
    with open(fname) as f:
        line = f.readline()
        while line:
            if(count % 10000 == 0):
                print(count)

            rec = json.loads(line) 
            futures[count] = rec['future']
            past[count] = rec['past']
            count += 1
            line = f.readline()
    return (futures, past)


print('Loading ....')

batch_size = get_num('./feed/count')

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
past = LSTM(128, return_sequences=True)(past_in)
past = Dropout(0.3)(past)
past = LSTM(128, return_sequences=False)(past_in)
past = Dense(units=32, activation='relu')(past)
past = Dropout(0.3)(past)
past = Dense(units=128, activation='relu')(past)

prediction = Dense(units=3, activation='softmax')(past)

model = Model(inputs=past_in, outputs=prediction)
model.compile('adam', 'categorical_crossentropy', metrics=['accuracy'])

# model.summary()

#
# Training
#
model.fit(train_X_past, train_Y, validation_split=0.3, epochs=EPOCHS, callbacks=[
    EarlyStopping(monitor='val_loss', patience=5),
    TensorBoard(log_dir='./logs', histogram_freq=0)
])
model.save(datetime.datetime.now().strftime('./models/%Y%m%d-%H%M.h5'))