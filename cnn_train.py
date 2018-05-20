import myenv
import numpy as np
import datetime
import argparse

from keras.models import  Model
from keras.layers import Input, Dense, Flatten, Dropout, Conv1D, MaxPooling1D
from keras.layers.merge import concatenate
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping, TensorBoard

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['train', 'continue', 'test'], default='train')
# parser.add_argument('--env-name', type=str, default='BreakoutDeterministic-v4')
# parser.add_argument('--weights', type=str, default=None)
args = parser.parse_args()

EPOCHS=20

MODEL_DIR = './cnn_model'
X_NPZ = './feed/cnn/x.npz'
Y_NPZ = './feed/cnn/y.npz'

x = np.load(X_NPZ)['arr_0']
y = to_categorical(np.load(Y_NPZ)['arr_0'], num_classes=3)

#
# Building Model
#
past_in = Input(shape=(x.shape[1], x.shape[2]))
past = Conv1D(64, 1, strides=1, padding='same', activation='relu')(past_in)
past = MaxPooling1D(2, padding='same')(past)
past = Dropout(0.2)(past)
past = Conv1D(64, 1, strides=1, padding='same', activation='relu')(past)
past = MaxPooling1D(2, padding='same')(past)
past = Dropout(0.2)(past)
past = Conv1D(64, 1, strides=1, padding='same', activation='relu')(past)
past = MaxPooling1D(2, padding='same')(past)
past = Dropout(0.2)(past)

past = Flatten()(past)
past = Dense(units=64, activation='relu')(past)
past = Dropout(0.2)(past)
past = Dense(units=32, activation='relu')(past)

# merged = concatenate([bids_layer, asks_layer])
# merged = Dropout(0.5)(merged)
# merged = Dense(units=16, activation='relu')(merged)
# prediction = Dense(units=3, activation='softmax')(merged)
# model = Model(inputs=[bids_layer_in, asks_layer_in], outputs=prediction)

prediction = Dense(units=3, activation='softmax')(past)

model = Model(inputs=past_in, outputs=prediction)
model.compile('adam', 'categorical_crossentropy', metrics=['accuracy'])


if args.mode == 'continue':
  model.load(MODEL_DIR + '/model.h5')

model.fit(x, y, validation_split=0.3, epochs=EPOCHS, callbacks=[
  EarlyStopping(monitor='val_loss', patience=5),
  # TensorBoard(log_dir='./logs', histogram_freq=0)
])
model.save(datetime.datetime.now().strftime(MODEL_DIR + '/%Y%m%d-%H%M.h5'))
model.save(MODEL_DIR + '/model.h5', overwrite=True)