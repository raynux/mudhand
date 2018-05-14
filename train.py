import myenv
import numpy as np
import gym
import datetime
import argparse

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['train', 'continue', 'test'], default='train')
# parser.add_argument('--env-name', type=str, default='BreakoutDeterministic-v4')
parser.add_argument('--weights', type=str, default=None)
args = parser.parse_args()


ENV_NAME = 'Market-v0'


# Get the environment and extract the number of actions.
env = gym.make(ENV_NAME)
# np.random.seed(123)
# env.seed(123)
nb_actions = env.action_space.n

print(env.observation_space)

# Next, we build a very simple model.
model = Sequential()
model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dense(nb_actions))
model.add(Activation('relu'))
print(model.summary())

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=60,
               target_model_update=1e-2, policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])


if args.mode == 'train':
  dqn.fit(env, nb_steps=100000, visualize=True, verbose=1)
  dqn.save_weights(datetime.datetime.now().strftime('./models/%Y%m%d-%H%M.h5f'))
  dqn.save_weights('./models/model.h5f')

elif args.mode == 'continue':
  dqn.load_weights('./models/model.h5f')
  dqn.fit(env, nb_steps=100000, visualize=True, verbose=1)
  dqn.save_weights(datetime.datetime.now().strftime('./models/%Y%m%d-%H%M.h5f'))

elif args.mode == 'test':
  dqn.test(env, nb_episodes=10, visualize=True)