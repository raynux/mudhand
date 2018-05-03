import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Conv1D, MaxPooling1D
from keras.utils import to_categorical

# bids = [
#     [
#         [0.1, 0.10],
#         [0.2, 0.20],
#         [0.3, 0.30],
#         [0.4, 0.40],
#     ],
#     [
#         [0.1, 0.10],
#         [0.2, 0.20],
#         [0.3, 0.30],
#         [0.4, 0.40],
#     ],
#     [
#         [0.1, 0.10],
#         [0.2, 0.20],
#         [0.3, 0.30],
#         [0.4, 0.40],
#     ],
#     [
#         [0.1, 0.10],
#         [0.2, 0.20],
#         [0.3, 0.30],
#         [0.4, 0.40],
#     ],
#     [
#         [0.1, 0.10],
#         [0.2, 0.20],
#         [0.3, 0.30],
#         [0.4, 0.40],
#     ],
#     [
#         [0.1, 0.10],
#         [0.2, 0.20],
#         [0.3, 0.30],
#         [0.4, 0.40],
#     ],
#     [
#         [0.1, 0.10],
#         [0.2, 0.20],
#         [0.3, 0.30],
#         [0.4, 0.40],
#     ],
#     [
#         [0.1, 0.10],
#         [0.2, 0.20],
#         [0.3, 0.30],
#         [0.4, 0.40],
#     ],
#     [
#         [0.1, 0.10],
#         [0.2, 0.20],
#         [0.3, 0.30],
#         [0.4, 0.40],
#     ],
# ]
# bids = np.array(bids)
#
# asks = [
#     [
#         [0.5, 0.50],
#         [0.6, 0.60],
#         [0.7, 0.70],
#         [0.8, 0.80],
#     ],
#     [
#         [0.5, 0.50],
#         [0.6, 0.60],
#         [0.7, 0.70],
#         [0.8, 0.80],
#     ],
#     [
#         [0.5, 0.50],
#         [0.6, 0.60],
#         [0.7, 0.70],
#         [0.8, 0.80],
#     ],
#     [
#         [0.5, 0.50],
#         [0.6, 0.60],
#         [0.7, 0.70],
#         [0.8, 0.80],
#     ],
#     [
#         [0.5, 0.50],
#         [0.6, 0.60],
#         [0.7, 0.70],
#         [0.8, 0.80],
#     ],
#     [
#         [0.5, 0.50],
#         [0.6, 0.60],
#         [0.7, 0.70],
#         [0.8, 0.80],
#     ],
#     [
#         [0.5, 0.50],
#         [0.6, 0.60],
#         [0.7, 0.70],
#         [0.8, 0.80],
#     ],
#     [
#         [0.5, 0.50],
#         [0.6, 0.60],
#         [0.7, 0.70],
#         [0.8, 0.80],
#     ],
#     [
#         [0.5, 0.50],
#         [0.6, 0.60],
#         [0.7, 0.70],
#         [0.8, 0.80],
#     ]
# ]
# asks = np.array(asks)

train_X = np.array([
    [
        [1, 2],
        [1, 2],
        [1, 2],
        [1, 2],
    ],
    [
        [1, 2],
        [1, 2],
        [1, 2],
        [1, 2],
    ],
    [
        [1, 2],
        [1, 2],
        [1, 2],
        [1, 2],
    ],
])

# train_Y = [1, 0, -1, 0, 0, 0, 1, -1, 1]
train_Y = [
    [
        [1]
    ],
    [
        [0]
    ],
    [
        [-1]
    ]
]
# train_Y = [1,0,-1]

train_Y = to_categorical(train_Y, num_classes=3)

# print(bids.shape)
# print(asks.shape)
print(train_X.shape)
print(train_Y.shape)

model = Sequential()
model.add(Conv1D(64, 8, strides=1, padding='same', input_shape=(4, 2), activation='relu'))
model.add(MaxPooling1D(2, padding='same'))
model.add(Conv1D(64, 8, strides=1, padding='same', activation='relu'))
model.add(MaxPooling1D(2, padding='same'))
model.add(Conv1D(32, 8, strides=1, padding='same', activation='relu'))
model.add(Dense(units=3, activation='softmax'))
model.compile('adam', 'categorical_crossentropy', metrics=['accuracy'])
# model.summary()

history = model.fit(train_X, train_Y, validation_split=0.1, epochs=1000)
