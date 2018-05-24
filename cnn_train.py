import myenv
import numpy as np
import datetime
import argparse

from keras.models import  Model, load_model
from keras.layers import Input, Dense, Flatten, Dropout, Conv1D, MaxPooling1D
from keras.layers.merge import concatenate
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping, TensorBoard, ModelCheckpoint

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['train', 'continue', 'test'], default='train')
# parser.add_argument('--env-name', type=str, default='BreakoutDeterministic-v4')
# parser.add_argument('--weights', type=str, default=None)
args = parser.parse_args()

EPOCHS=1000

MODEL_DIR = './cnn_model'
feed = np.load('./feed/cnn/data.npz')

y = to_categorical(feed['y'], num_classes=3)
x1 = feed['x1']
x2 = feed['x2']
x3 = feed['x3']
x4 = feed['x4']
x5 = feed['x5']
x = [x1, x2, x3, x4, x5]

#
# Building Model
#
def build_branch(x):
  layer_in = Input(shape=(x.shape[1], x.shape[2]))
  layer = Conv1D(64, kernel_size=5, strides=1, padding='same', activation='relu')(layer_in)
  layer = MaxPooling1D(2, padding='same')(layer)
  layer = Dropout(0.3)(layer)
  layer = Conv1D(64, kernel_size=5, strides=1, padding='same', activation='relu')(layer)
  layer = MaxPooling1D(2, padding='same')(layer)
  layer = Dropout(0.3)(layer)
  layer = Conv1D(64, kernel_size=5, strides=1, padding='same', activation='relu')(layer)
  layer = MaxPooling1D(2, padding='same')(layer)
  layer = Dropout(0.3)(layer)
  layer = Flatten()(layer)
  layer = Dense(16, activation='relu')(layer)
  return (layer_in, layer)


if args.mode == 'continue':
  model = load_model(MODEL_DIR + '/model.h5')
else:
  x1_in, x1_layer = build_branch(x1)
  x2_in, x2_layer = build_branch(x2)
  x3_in, x3_layer = build_branch(x3)
  x4_in, x4_layer = build_branch(x4)
  x5_in, x5_layer = build_branch(x5)

  branches_in = [x1_in, x2_in, x3_in, x4_in, x5_in]
  branches = [x1_layer, x2_layer, x3_layer, x4_layer, x5_layer]

  merged = concatenate(branches)
  merged = Dropout(0.3)(merged)
  merged = Dense(units=16, activation='relu')(merged)
  prediction = Dense(units=3, activation='softmax')(merged)

  model = Model(inputs=branches_in, outputs=prediction)
  model.compile('adam', 'categorical_crossentropy', metrics=['accuracy'])

print(model.summary())

model.fit(x, y, validation_split=0.3, epochs=EPOCHS, callbacks=[
  EarlyStopping(monitor='val_loss', patience=10),
  ModelCheckpoint(
    filepath=datetime.datetime.now().strftime(MODEL_DIR + '/%Y%m%d-%H%M.h5'),
    save_best_only=True
  ),
  # TensorBoard(log_dir='./logs', histogram_freq=0)
])
model.save(MODEL_DIR + '/model.h5', overwrite=True)