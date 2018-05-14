import gym
import numpy as np
import gym.spaces as spaces

class Position():
  POS_BOOL_INDEX = 0
  POS_PRICE_INDEX = 1

  NO_POSITION = 0
  LONG_POSITION = 1
  SHORT_POSITION = 2

  INVALID_REWARD = -100000

  def __init__(self, SEQ_LEN):
    self.SEQ_LEN = SEQ_LEN
    self.reset()

  def buy(self, price):
    if self.has_short_position():   # clear position
      reward = self.position_price() - price
      self.set_position(self.NO_POSITION)
      return reward
    elif self.has_no_position():    # get a long position
      self.set_position(self.LONG_POSITION, price)
      return 0

    return self.INVALID_REWARD  # invalid operation

  def sell(self, price):
    if self.has_long_position():  # clear position
      reward = price - self.position_price()
      self.set_position(self.NO_POSITION)
      return reward
    elif self.has_no_position():    # get a long position
      self.set_position(self.LONG_POSITION, price)
      return 0

    return self.INVALID_REWARD  # invalid operation

  def reset(self):
    self.state = np.zeros(self.SEQ_LEN)

  def position_price(self):
    return self.state[self.POS_PRICE_INDEX]

  def set_position(self, pos_type, price=0):
    self.state[self.POS_BOOL_INDEX] = pos_type
    self.state[self.POS_PRICE_INDEX] = price

  def has_no_position(self):
    return (self.state[self.POS_BOOL_INDEX] == self.NO_POSITION)

  def has_long_position(self):
    return (self.state[self.POS_BOOL_INDEX] == self.LONG_POSITION)

  def has_short_position(self):
    return (self.state[self.POS_BOOL_INDEX] == self.SHORT_POSITION)


class Market(gym.Env):
  metadata = {'render.modes': ['human']}

  HIST = np.array([
    0,1,2,3,4,6,4,3,2,1,
    0,1,2,3,4,8,4,3,2,1,
    0,1,2,3,4,9,4,3,2,1,
    0,1,2,3,4,5,4,3,2,1,
    0,1,2,3,4,6,4,3,2,1,
    0,1,2,3,4,7,4,3,2,1,
    0,1,2,3,4,8,4,3,2,1,
    0,1,2,3,4,5,4,3,2,1,
    0,1,2,3,4,6,4,3,2,1,
    0,1,2,3,4,5,4,3,2,1,
    0,1,2,3,4,7,4,3,2,1,
    0,1,2,3,4,5,4,3,2,1,
    0,1,2,3,4,8,4,3,2,1,
    0,1,2,3,4,5,4,3,2,1,
    0,1,2,3,4,7,4,3,2,1,
    0,1,2,3,4,5,4,3,2,1,
    0,1,2,3,4,9,4,3,2,1,
    0,1,2,3,4,5,4,3,2,1,
    0,1,2,3,4,6,4,3,2,1,
    0,1,2,3,4,5,4,3,2,1,
  ])
  SEQ_LEN = 5

  STAY = 0
  BUY = 1
  SELL = 2

  def __init__(self):
    super().__init__()

    self.HIST_LEN = self.HIST.shape[0]
    self.position = Position(self.SEQ_LEN)

    self.action_space = spaces.Discrete(3) 
    self.observation_space = spaces.Box(low=0, high=10, shape=(2, self.SEQ_LEN), dtype=np.int32)
    self.reset()

  def reset(self):
    self.done = False
    self.seq_index = 0
    self.position.reset()
    return self._observe()

  def step(self, action):
    current_price = self.HIST[self.seq_index + self.SEQ_LEN]
    reward = 0

    if action == self.BUY:
      reward = self.position.buy(current_price)
    elif action == self.SELL:
      reward = self.position.sell(current_price)

    self.seq_index += 1

    if self.seq_index >= self.HIST_LEN - self.SEQ_LEN:
      self.done = True

    return self._observe(), reward, self.done, {}


  def render(self, mode='human', close=False):
    # print(self.position)
    pass

  def _observe(self):
    visible_seq = self.HIST[self.seq_index:self.seq_index + self.SEQ_LEN]
    return np.array([visible_seq, self.position.state], dtype=np.int32)
