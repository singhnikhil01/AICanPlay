import torch
import random
import numpy as np
from collections import deque
from gameplayAI import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self): 
        self.n_games = 0 
        self.epsilon = 0 #randomness 
        self.gamma = 0.9 #discount rate 
        self.memory = deque(maxlen=MAX_MEMORY) # popleft 
        self.model = Linear_QNet(11,256,3) #size_of_state, hiddensize , output__possible 
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma) 
        # TODO: model,trainer 


    # finding all the state of the game 
    def get_state(self, game):

        head = game.snake[0] #point the snake head

        #position of the snake head
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)
        
        #state of the direction 
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
            ]

        return np.array(state, dtype=int) #[danger staraight, danger-right, dangerleft , move directions , food locations]


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

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1

            #now start predecting the states 
        else:
            #A torch.Tensor is a multi-dimensional matrix containing elements of a single data type.
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            #Returns the indices of the maximum value of all elements in the input tensor
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move 


#Training the model 
def train():
    plot_scores = [] #scores to be ploted 
    plot_mean_scores = [] #mean of the scores  line 
    total_score = 0 #total score 
    record = 0 #a recored of scores 
    agent = Agent() #initialize agent class 
    game = SnakeGameAI() #initialize the game class 
    while True:

        # get old state
        state_old = agent.get_state(game)  #get the initial state of the game 

        # get move
        final_move = agent.get_action(state_old) #get the move for that state 

        # perform move and get new state
        reward, done, score = game.play_step(final_move) #perform that move in the game 
        state_new = agent.get_state(game) #get a new state after performing the move

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done) #training the short memory 

        # remember
        agent.remember(state_old, final_move, reward, state_new, done) #remember the moves and states 

        #when game is finished
        if done:
            # train long memory, plot result
            game.reset() #reset the game 
            agent.n_games += 1 #add one in the number of games played 
            agent.train_long_memory() #save the data in the long train in the data stracture, final data after game completed 


            #if new record is game , (high score), save the model state 
            if score > record:
                record = score
                #save the model 
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            #updates the result
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


#starting from training the model 
if __name__ =='__main__':
    train()