import torch
import random
import numpy as np
import itertools
import os
from collections import deque
from main import AbstractCar, PlayerCar, GameAI
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.01

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 1 # randomness
        self.gamma = 0.95 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.steps_since_checkpoint = 0
        self.model = Linear_QNet(13,150,150,150,5)


        # model_folder_path = './model'
        # model_file_path = os.path.join(model_folder_path, 'mymodel.pth')

        # if os.path.exists('.\model\mymodel.pth'):
        #     #print("Loading pre-existing model...")
        #     model.load_state_dict(torch.load('.\model\mymodel.pth'))
        #     model.eval()
        # self.model = model
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        


    def get_state(self, game):
        

        state = game.get_state()

        return np.array(state, dtype=float)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    #def train_short_memory(self, state, action, reward, next_state, done,game):
    def train_short_memory(self):
        if len(self.memory)>self.steps_since_checkpoint:
            mini_sample = list(itertools.islice(self.memory, len(self.memory)-1-self.steps_since_checkpoint, len(self.memory)-1))
            states, actions, rewards, next_states, dones = zip(*mini_sample)

            self.trainer.train_step(states, actions, [10]*len(dones), next_states, dones)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        #self.epsilon *= 0.9997
        # if 10000<self.n_games:
        #     self.epsilon = 0.05
        final_move = [0,0,0, 0,0]
        if 0 < self.epsilon:
            #print("guess:")
            move = random.randint(0, 4)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move



def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = GameAI()
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)
        agent.steps_since_checkpoint += 1
        #print(final_move)
        # perform move and get new state
        reward, done, score = game.play_step(final_move)


        if reward == 10:
            agent.train_short_memory()
            agent.steps_since_checkpoint = 0

        #print("Score:",score,"reward:",reward)
        state_new = agent.get_state(game)
        
        # train short memory
        #agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            game.reset()
            agent.epsilon *= 0.9997
            print(agent.epsilon)
            agent.n_games += 1
            agent.steps_since_checkpoint = 0
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()
            if agent.n_games % 1000 == 0:
                agent.model.save()


            #print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()