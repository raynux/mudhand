import gym
import numpy as np
import gym.spaces as spaces
import pandas as pd

X_NPZ = './feed/dqn/x.npz'
Y_NPZ = './feed/dqn/y.npz'
INVALID_CHOICE_REWARD = -1000
NO_TRADE_REWARD = -1000
NOOP_REWARD = 0
DECISION_REWARD = 0

class Position():
  POS_BOOL_INDEX = 0
  POS_PRICE_INDEX = 1

  NO_POSITION = 0
  LONG_POSITION = 1
  SHORT_POSITION = 2

  def __init__(self, shape):
    self.shape = shape
    self.reset()

  def buy(self, price):
    if self.has_position():
      return INVALID_CHOICE_REWARD  # invalid operation

    self.set_position(self.LONG_POSITION, price)
    return DECISION_REWARD

  def sell(self, price):
    if self.has_position():
      return INVALID_CHOICE_REWARD  # invalid operation

    self.set_position(self.SHORT_POSITION, price)
    return DECISION_REWARD

  def close(self, price):
    if self.has_long_position():
      reward = self.position_price() - price
      reward += DECISION_REWARD
      # print('BUY : ' + str(reward) + ' : ' + str(self.position_price()) + ' : ' + str(price))
      self.set_position(self.NO_POSITION)
      return reward
    elif self.has_short_position():
      reward = price - self.position_price()
      reward += DECISION_REWARD
      # print('SELL : ' + str(reward) + ' : ' + str(self.position_price()) + ' : ' + str(price))
      self.set_position(self.NO_POSITION)
      return reward

    return INVALID_CHOICE_REWARD  # invalid operation

  def reset(self):
    self.state = np.zeros(self.shape)

  def position_price(self):
    return int(self.state[0][self.POS_PRICE_INDEX])

  def set_position(self, pos_type, price=0):
    self.state[0][self.POS_BOOL_INDEX] = pos_type
    self.state[0][self.POS_PRICE_INDEX] = price

  def has_position(self):
    return (self.state[0][self.POS_BOOL_INDEX] != self.NO_POSITION)

  def has_long_position(self):
    return (self.state[0][self.POS_BOOL_INDEX] == self.LONG_POSITION)

  def has_short_position(self):
    return (self.state[0][self.POS_BOOL_INDEX] == self.SHORT_POSITION)


class Market(gym.Env):
  metadata = {'render.modes': ['human']}

  SEQ_LEN = 240
  VISIBLE_LEN = 60
  HIGH = 100

  STAY = 0
  BUY = 1
  SELL = 2
  CLOSE = 3

  def __init__(self):
    super().__init__()

    self.x = np.load(X_NPZ)['arr_0']
    self.y = np.load(Y_NPZ)['arr_0']
    self.position = Position((self.VISIBLE_LEN, self.x.shape[1]))

    self.action_space = spaces.Discrete(4) 
    self.observation_space = spaces.Box(low=0, high=self.HIGH, shape=(2, self.VISIBLE_LEN, self.x.shape[1]), dtype=np.float32)
    self.reset()

  def reset(self):
    self.done = False
    self.init_seq()
    self.position.reset()
    return self._observe()

  def step(self, action):
    current_price = self.current_price()
    reward = NOOP_REWARD

    if action == self.BUY:
      reward = self.position.buy(current_price)
    elif action == self.SELL:
      reward = self.position.sell(current_price)
    elif action == self.CLOSE:
      reward = self.position.close(current_price)
      # self.done = True
    # else:   # STAY
    #   print('STAY [ ' + str(self.seq_index) + ' ] : ' + str(current_price))

    self.seq_index += 1

    if self.seq_index >= self.SEQ_LEN - self.VISIBLE_LEN:
      reward = NO_TRADE_REWARD
      self.done = True

    # if reward > 0:
    #   print(str(action) + ' : ' + str(current_price) + ' : ' + str(reward))

    return self._observe(), reward, self.done, {}


  def render(self, mode='human', close=False):
    # if self.step_decition != self.STAY:
    #   print('[ ' + str(self.step_decition) + ' ] ' + str(self.step_reward))
    pass

  def _observe(self):
    visible_seq = np.array(self.seq[self.seq_index:self.seq_index + self.VISIBLE_LEN], dtype=np.float32)
    return np.array([visible_seq, self.position.state], dtype=np.float32)

  def init_seq(self):
    self.seq_index = 0
    start_pos = np.random.randint(self.x.shape[0] - self.SEQ_LEN)
    self.seq = self.x[start_pos:start_pos + self.SEQ_LEN]

  def current_price(self):
    return self.y[self.seq_index + self.VISIBLE_LEN]