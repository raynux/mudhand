import myenv
import numpy as np
import gym
import datetime
import argparse

from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, TensorBoard

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['train', 'continue', 'test'], default='train')
# parser.add_argument('--env-name', type=str, default='BreakoutDeterministic-v4')
# parser.add_argument('--weights', type=str, default=None)
args = parser.parse_args()

STEPS = 100000
WINDOW_LENGTH = 1

ENV_NAME = 'Market-v0'
MODEL_DIR = './dqn_model'


# Get the environment and extract the number of actions.
env = gym.make(ENV_NAME)
# np.random.seed(123)
# env.seed(123)
nb_actions = env.action_space.n

print(env.observation_space)

# Next, we build a very simple model.
model = Sequential()
model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
model.add(Dense(256, activation='relu'))
model.add(Dense(256, activation='relu'))
model.add(Dense(256, activation='relu'))
model.add(Dense(nb_actions, activation='tanh'))
# print(model.summary())

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=STEPS, window_length=WINDOW_LENGTH)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=60,
               target_model_update=1e-2, policy=policy, enable_dueling_network=True, dueling_type='avg')
dqn.compile(Adam(), metrics=['mae'])


def fit_and_save(agent):
  agent.fit(env, nb_steps=STEPS, visualize=False, verbose=1, callbacks=[
    # TensorBoard(log_dir='./logs', histogram_freq=0),
  ])
  agent.save_weights(datetime.datetime.now().strftime(MODEL_DIR + '/%Y%m%d-%H%M.h5f'))
  agent.save_weights(MODEL_DIR + '/model.h5f', overwrite=True)

if args.mode == 'test':
  dqn.load_weights(MODEL_DIR + '/model.h5f')
  dqn.test(env, nb_episodes=100, visualize=False)
else:
  if args.mode == 'continue':
    dqn.load_weights(MODEL_DIR + '/model.h5f')
  
  while True:
    fit_and_save(dqn)
    dqn.test(env, nb_episodes=10, visualize=False)
