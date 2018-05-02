import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

# INPUT
# price  : price
# bids   : [[diff, size], ...]
# asks   : [[diff, size], ...]
# future :
#   0 : stays within the range
#   1 : price goes up
#   2 : price goes down
