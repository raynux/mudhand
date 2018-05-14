import gym
import numpy as np
import gym.spaces as spaces

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
    self.pos_state = np.zeros(self.SEQ_LEN)

    self.action_space = spaces.Discrete(3) 
    self.observation_space = spaces.Box(low=0, high=10, shape=(2, self.SEQ_LEN), dtype=np.float)
    self.reset()

  def reset(self):
    self.done = False
    self.seq_index = 0
    self.position = None
    return self._observe()

  def step(self, action):
    current_price = self.HIST[self.seq_index + self.SEQ_LEN]
    reward = 0

    if action == self.STAY:
      pass

    elif action == self.BUY:
      if self.position == None:
        self.position = current_price
      else:  # violation!
        reward = -1

    elif action == self.SELL:
      if self.position != None:
        reward = current_price - self.position
        self.position = None
      else:  # violation!
        reward = -1

    self.seq_index += 1

    if self.seq_index >= self.HIST_LEN - self.SEQ_LEN:
      self.done = True

    return self._observe(), reward, self.done, {}


  def render(self, mode='human', close=False):
    # print(self.position)
    pass

  def _observe(self):
    visible_seq = self.HIST[self.seq_index:self.seq_index + self.SEQ_LEN]

    if self.position == None:
      self.pos_state[0] = 0
      self.pos_state[1] = 0
    else:
      self.pos_state[0] = 1
      self.pos_state[1] = self.position

    return [visible_seq, self.pos_state]
