import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
#arial.ttf is the font package
font = pygame.font.Font('arial.ttf', 25) #font size of the score things

#reset function 
#rewards the function 
#play(actions) performed by our model  --> direction
#game iteration 
# is_collision  


#change direction I guess 
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y') #dictionary type thing 

# diffetrnt rgb colors initilised 
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20 #size of the block , that is snake and the food 
SPEED = 5 #speed of the snake 


#snake game class

class SnakeGameAI:
    def __init__(self, w=640, h=480):# w and h is the width and height of the frame 
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h)) #display the frame of width w and height h 
        pygame.display.set_caption('Snake AI Model') #caption of the game 
        self.clock = pygame.time.Clock() #can say a refresh rate of the game 
        
        # init game state
        self.direction = Direction.RIGHT # direction from the direction class 
        
        self.head = Point(self.w/2, self.h/2) #instial position of the blocks 
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        self.score = 0 #initial score of the game 
        self.food = None #may be the initial position of the game 
        self._place_food() # calling place food class that will place food randomly 
    
        
    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y) # x and y coordinates is totally random 

        #if the food will apperar with in snake itself re-run the code to place the food to another location 
        if self.food in self.snake:
            self._place_food()
        
    def play_step(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #if we quit exit from the game 
                pygame.quit()
                quit()
            
            #key events listening 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.direction = Direction.DOWN
        
        # 2. move according to the key event 
        self._move(self.direction) # update the head and change the direction as given by self.direction 
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        game_over = False

        #if game over return game_over,score 
        if self._is_collision():
            game_over = True
            return game_over, self.score
            
        # 4. place new food or just move, if the head touches the food 
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED) #update the clock 
        # 6. return game over and score
        return game_over, self.score
    
    def _is_collision(self):
        # hits boundary
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            return True

        # hits itself
        if self.head in self.snake[1:]:
            return True
        
        return False
        
    def _update_ui(self):
        self.display.fill(BLACK) #Black background 
        
        #all the blocks in the snake 
        for pt in self.snake:
            #draw a rectange to appear it as snake
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            #snake is made up of two colours , one is inside another one 
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        #its a recangle for the food 
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        #it's the score written in the frame
        text = font.render("Score: " + str(self.score), True, WHITE)


        self.display.blit(text, [0, 0]) # position of the score board in the game 
        pygame.display.flip() ##update the full screen surface to the screen
        

    def _move(self, direction):

        #change the block size to move the snake
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)
            

if __name__ == '__main__':
    game = SnakeGameAI()
    
    # game loop
    while True:
        game_over, score = game.play_step()
        
        if game_over == True:
            # pygame.quit()
            pygame.init()
            break
        
    print('Final Score', score)    
    pygame.quit()