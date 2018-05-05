import json
import datetime
import numpy as np
from keras.models import  Model
from keras.layers import Input, Dense, Flatten, Dropout, Conv1D, MaxPooling1D
from keras.layers.merge import concatenate
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping, TensorBoard

EPOCHS=10

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
train_batch_size = get_batch_size('./feed/train_count')
test_batch_size = get_batch_size('./feed/test_count')

(train_Y, train_X_ladder) = load_feed(train_batch_size, './feed/train')
train_Y = to_categorical(train_Y, num_classes=3)

(test_Y, test_X_ladder) = load_feed(test_batch_size, './feed/test')
test_Y = to_categorical(test_Y, num_classes=3)

print(train_Y.shape)
print(train_X_ladder.shape)
print(test_Y.shape)
print(test_X_ladder.shape)

ladder_in = Input(shape=(train_X_ladder.shape[1], train_X_ladder.shape[2]))
ladder = Conv1D(64, 8, strides=1, padding='same', activation='relu')(ladder_in)
ladder = MaxPooling1D(2, padding='same')(ladder)
ladder = Dropout(0.3)(ladder)
ladder = Conv1D(64, 8, strides=1, padding='same', activation='relu')(ladder)
ladder = MaxPooling1D(2, padding='same')(ladder)
ladder = Dropout(0.3)(ladder)

ladder = Flatten()(ladder)
ladder = Dense(units=32, activation='relu')(ladder)
ladder = Dropout(0.3)(ladder)
ladder = Dense(units=32, activation='relu')(ladder)

# merged = concatenate([bids_layer, asks_layer])
# merged = Dropout(0.5)(merged)
# merged = Dense(units=16, activation='relu')(merged)
# prediction = Dense(units=3, activation='softmax')(merged)
# model = Model(inputs=[bids_layer_in, asks_layer_in], outputs=prediction)

prediction = Dense(units=3, activation='softmax')(ladder)

model = Model(inputs=ladder_in, outputs=prediction)
model.compile('adam', 'categorical_crossentropy', metrics=['accuracy'])

model.summary()

model.fit(train_X_ladder, train_Y, validation_data=(test_X_ladder, test_Y), epochs=EPOCHS, callbacks=[
    EarlyStopping(monitor='loss', patience=3),
    TensorBoard(log_dir='./logs', histogram_freq=0)
])
model.save(datetime.datetime.now().strftime('./models/%Y%m%d-%H%M.h5'))
