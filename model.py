import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import os

class DeepQNetwork(nn.Module):
    
    def __init__(self, lr, input_dims, hidden_layer_1_dims, hidden_layer_2_dims,
                 n_actions):
        super(DeepQNetwork, self).__init__()
        self.input_dims = input_dims
        self.hidden_layer_1_dims = hidden_layer_1_dims
        self.hidden_layer_2_dims = hidden_layer_2_dims
        self.n_actions = n_actions

        self.input_layer = nn.Linear(*self.input_dims, self.hidden_layer_1_dims)
        self.hidden_layer_1 = nn.Linear(self.hidden_layer_1_dims, self.hidden_layer_2_dims)
        self.hidden_layer_2 = nn.Linear(self.hidden_layer_2_dims, self.n_actions)

        self.optimizer = optim.Adam(self.parameters(), lr=lr)
        self.loss = nn.MSELoss()
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)



    def forward(self, state):

        x = F.relu(self.input_layer(state))
        x = F.relu(self.hidden_layer_1(x))
        actions = self.hidden_layer_2(x)

        return actions
    


    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        T.save(self.state_dict(), file_name)



class Agent:
    def __init__(self, gamma, epsilon, lr, input_dims, batch_size, n_actions,
                 max_mem_size=100000, eps_end=0.05, eps_dec=0.0025):
        self.gamma = gamma
        self.epsilon = epsilon
        self.eps_min = eps_end
        self.eps_dec = eps_dec
        self.lr = lr
        self.action_space = [i for i in range(n_actions)]
        self.mem_size = max_mem_size
        self.batch_size = batch_size
        self.mem_cntr = 0
        self.iter_cntr = 0
        self.replace_target = 100

        self.primary_nn = DeepQNetwork(lr, n_actions=n_actions,
                                   input_dims=input_dims,hidden_layer_1_dims=256, hidden_layer_2_dims=256)
        self.target_nn = DeepQNetwork(lr, n_actions=n_actions,
                                   input_dims=input_dims , hidden_layer_1_dims=256 , hidden_layer_2_dims=256)
        
        self.state_memory = np.zeros((self.mem_size, *input_dims),dtype=np.float32)
        self.new_state_memory = np.zeros((self.mem_size, *input_dims),dtype=np.float32)
        self.action_memory = np.zeros(self.mem_size, dtype=np.int32)
        self.reward_memory = np.zeros(self.mem_size, dtype=np.float32)
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.bool_)



    def save(self):
        self.primary_nn.save()



    def load(self):
        if os.path.exists(os.path.join('./model','model.pth')):
            self.primary_nn.load_state_dict(T.load(os.path.join('./model','good_circle.pth')))
            self.target_nn.load_state_dict(T.load(os.path.join('./model','good_circle.pth')))



    def store_transition(self, state, action, reward, state_, terminal):
        index = self.mem_cntr % self.mem_size
        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.reward_memory[index] = reward
        self.action_memory[index] = action
        self.terminal_memory[index] = terminal

        self.mem_cntr += 1



    def choose_action(self, observation):
        if np.random.random() > self.epsilon:
            state = T.tensor([observation]).to(self.primary_nn.device)
            actions = self.primary_nn.forward(state)
            action = T.argmax(actions).item()
        else:
            action = np.random.choice(self.action_space)

        return action
    


    def update_target_net(self):
        self.target_nn.load_state_dict(self.primary_nn.state_dict())



    def create_batches(self,batch):
        state_batch = T.tensor(self.state_memory[batch]).to(self.primary_nn.device)
        new_state_batch = T.tensor( self.new_state_memory[batch]).to(self.primary_nn.device)
        action_batch = self.action_memory[batch]
        reward_batch = T.tensor(
                self.reward_memory[batch]).to(self.primary_nn.device)
        terminal_batch = T.tensor(
                self.terminal_memory[batch]).to(self.primary_nn.device)
        
        return state_batch, new_state_batch, action_batch, reward_batch, terminal_batch



    def learn(self):
        
        if self.mem_cntr < self.batch_size:
            return

        self.primary_nn.optimizer.zero_grad()

        max_mem = min(self.mem_cntr, self.mem_size)

        batch = np.random.choice(max_mem, self.batch_size, replace=False)
        batch_index = np.arange(self.batch_size, dtype=np.int32)
        
        state_batch, new_state_batch, action_batch, reward_batch, terminal_batch = self.create_batches(batch=batch)


        q_eval = self.primary_nn.forward(state_batch)[batch_index, action_batch]
        q_next = self.target_nn.forward(new_state_batch)
        q_next[terminal_batch] = 0.0

        q_target = reward_batch + self.gamma*T.max(q_next, dim=1)[0]

        loss = self.primary_nn.loss(q_target, q_eval).to(self.primary_nn.device)
        loss.backward()
        self.primary_nn.optimizer.step()


        self.iter_cntr += 1
