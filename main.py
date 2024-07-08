from game.game import GameAI 
from model import Agent
import numpy as np
import collections
from game.maps import Map_1
import csv


if __name__ == '__main__':
    game = GameAI(FPS=10_000,map=Map_1)
    agent = Agent(gamma=0.99, epsilon=1.0, batch_size=100, n_actions=6, eps_end=0.01,
                  input_dims=[13], lr=0.001)
    # agent.load()
    scores = collections.deque([])
    game_no = 0
    best_score = 0

    csvfile = open('stats.csv','w',newline='')

    writer = csv.writer(csvfile)
    writer.writerow(['episode','score','average score','epsilon'])

    

    # training loop
    while True:
        score = 0
        done = False
        observation = game.get_state()

        while not done:

            # choose action, receive observation
            action = agent.choose_action(observation)
            a = [0,0,0,0,0,0]
            a[action] = 1
            reward, done, score = game.play_step(a)
            observation_ = game.get_state()

            # store previous data for replay learning
            agent.store_transition(observation, action, reward, observation_, done)
            agent.learn()

            observation = observation_


        game.reset()
        agent.learn_big_batch(batch_size=10_000)
        
        # update epsilon value
        agent.epsilon = agent.epsilon - agent.eps_dec \
            if agent.epsilon > agent.eps_min else agent.eps_min
   
        # adjust list of scores and average score
        scores.append(score)
        if len(scores)>100:
            scores.popleft()
        avg_score = np.mean(scores)

        # print info to console
        print('episode ', game_no, 'score %.2f' % score,
                'average score %.2f' % avg_score,
                'epsilon %.2f' % agent.epsilon)
        writer.writerow([game_no,score,avg_score,agent.epsilon])
        
        game_no += 1

        if score > best_score:
            best_score = score
            agent.save()
        if game_no % 10 == 0:
            agent.update_target_net()
            agent.save()