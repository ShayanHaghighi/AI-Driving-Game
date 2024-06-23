import pygame
import random
import math
import time
from maps import Map_1
from helper import blit_rotate_center
 
LEFT,RIGHT,FORWARD,BOOST,BACKWARD = 0,1,2,3,4



class AbstractCar:
    def __init__(self, max_velocity=5, rotation_vel=7,drift=0.9,acceleration=0.1,initial_angle=math.pi/2,start_pos=(700, 704)):

        
        self.initial_angle = initial_angle
        self.drift = drift
        self.acceleration = acceleration
        self.x, self.y = start_pos
        self.rotation_vel = rotation_vel*math.pi/180
        self.max_velocity = max_velocity
        

        
        self.img = self.IMG
        self.boosting_img = self.BOOSTING_IMG

        self.current_speed = 0
        
        self.angle_headed = 0
        
        self.angle_facing = initial_angle



    def rotate(self, left=False, right=False):
        if left:
            self.angle_facing = (self.angle_facing + self.rotation_vel) 
        elif right:
            self.angle_facing = (self.angle_facing - self.rotation_vel)



    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), math.degrees(self.angle_facing))



    def bounce(self):
        self.angle_headed = (self.angle_headed + math.pi) 
        self.angle_facing = (self.angle_facing + math.pi) 
        self.current_speed *0.5
        self.update_position()
            


    def move_forward(self):
        if self.current_speed > self.max_velocity:
            self.current_speed *= 0.95
        self.update_position(accelerating=True)



    def move_backward(self):
        if self.current_speed > self.max_velocity/4:
            self.current_speed *= 0.95
        self.update_position(accelerating=True,reversing=True)



    def add_vectors(self,vector1, vector2):
        
        delta_x = (math.sin(vector1[0])*vector1[1] + math.sin(vector2[0])*vector2[1])
        delta_y = (math.cos(vector1[0])*vector1[1] + math.cos(vector2[0])*vector2[1])

        angle = math.atan2(delta_x,delta_y)
        magnitude = math.sqrt(delta_x**2+delta_y**2)

        return angle,magnitude



    def update_position(self,accelerating=False,reversing=False):
        if self.current_speed == 0 and not accelerating:
            self.angle_headed = 0
            return
        else:
            current_angle = self.angle_facing
            current_acceleration = self.acceleration

            if not accelerating:

                
                self.current_speed *= 0.95
                current_acceleration = 0

            elif reversing:
                
                current_angle = (self.angle_facing - math.pi)

        
        momentum_vector = (self.angle_headed,self.current_speed)

        
        engine_force_vector = (current_angle,current_acceleration)

        
        self.angle_headed,self.current_speed = self.add_vectors(momentum_vector,engine_force_vector)

        vertical = math.cos((self.angle_headed)) * self.current_speed
        horizontal = math.sin((self.angle_headed)) * self.current_speed

        self.y -= vertical
        self.x -= horizontal



    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi



    def reset(self):
        self.x, self.y = self.START_POS
        self.angle_facing = math.pi/2
        self.current_speed = 0
        self.angle_headed = 0



class PlayerCar(AbstractCar):
    IMG = Map_1.CAR
    BOOSTING_IMG = Map_1.BOOST_CAR
    START_POS = (700, 704)



class GameAI:

    def __init__(self,FPS,map):
        self.map = map
        pygame.display.set_caption("Racing Game!")
        self.screen = pygame.display.set_mode((map.WIDTH, map.HEIGHT))
        self.WIN = pygame.Surface((map.WIDTH, map.HEIGHT))
        self.clock = pygame.time.Clock()
        self.FPS = FPS

        self.AI_car = PlayerCar(max_velocity=3, rotation_vel=7)

        self.passing_finish_line = False

        
        self.checkpoints = [
                            ((663, 650),(666, 783)),
                            ((600, 780),(605, 647)),
                            ((556, 639),(532, 774)),
                            ((464, 766),(497, 632)),
                            ((435, 614),(381, 747)),
                            ((313, 729),(361, 602)),
                            ((298, 573),(192, 696)),
                            ((135, 660),(256, 545)),
                            ((225, 501),(64, 582)),
                            ((28, 531),(216, 477)),
                            ((208, 436),(22, 438)),
                            ((22, 399),(212, 406)),
                            ((214, 368),(48, 293)),
                            ((88, 235),(233, 328)),
                            ((255, 302),(165, 170)),
                            ((209, 149),(284, 261)),
                            ((286, 112),(347, 235)),
                            ((391, 219),(352, 92)),
                            ((403, 74),(442, 192)),
                            ((487, 186),(477, 57)),
                            ((558, 36),(570, 172)),
                            ((636, 167),(635, 39)),
                            ((705, 39),(703, 164)),
                            ((772, 168),(784, 30)),
                            ((847, 32),(832, 171)),
                            ((888, 169),(916, 49)),
                            ((992, 58),(964, 198)),
                            ((1005, 220),(1090, 93)),
                            ((1153, 120),(1066, 265)),
                            ((1117, 298),(1265, 233)),
                            ((1296, 276),(1140, 327)),
                            ((1154, 377),(1328, 365)),
                            ((1334, 424),(1151, 412)),
                            ((1164, 483),(1334, 520)),
                            ((1305, 601),(1146, 531)),
                            ((1099, 580),(1214, 710)),
                            ((1138, 739),(1060, 616)),
                            ((995, 626),(1070, 762)),
                            ((992, 774),(950, 640)),
                            ((888, 647),(896, 779)),
                            ((848, 784),(838, 651)),
                            ((782, 653),(784, 791)),
                            ]
        self.unpassed_checkpoints = [True] * len(self.checkpoints)
        
        
        self.line_angles = [0,math.pi/4,math.pi/2,3*math.pi/4,math.pi,5*math.pi/4,3*math.pi/2,7*math.pi/4]
        self.distances = [0] * len(self.line_angles)
        self.detect_lines()

        self.score = 0
        self.num_frames = 0

        

    def shake_screen(self):
        xOffset = random.randint(-1, 1)
        yOffset = random.randint(-1, 1)
        self.screen.blit(self.WIN, (xOffset, yOffset))

        pygame.display.update()

    
    def check_line_intersection(self,image, start, end, offset=(0,0)):
            x1, y1 = start
            x2, y2 = end

            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1
            err = dx - dy

            while x1 != x2 or y1 != y2:
                
                if 0 <= x1-offset[0] < image.get_width() and 0 <= y1-offset[1] < image.get_height():
                    pixel_alpha = image.get_at((int(x1-offset[0]), int(y1-offset[1])))[3]   
                    if pixel_alpha > 0:
                        return (x1,y1)

                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x1 += sx
                if e2 < dx:
                    err += dx
                    y1 += sy

            



    
    def passed_checkpoints(self):
        for i,checkpoint in enumerate(self.checkpoints):
            if (self.check_line_intersection(self.AI_car.img,checkpoint[0],checkpoint[1],(self.AI_car.x,self.AI_car.y))) != None:
                if self.unpassed_checkpoints[i]:
                    self.unpassed_checkpoints[i] = False
                    return True



    
    def detect_lines(self):
        max_line_length = 400

        for i,angle in enumerate(self.line_angles):

            
            car_width = self.AI_car.img.get_rect().width/2
            car_height = self.AI_car.img.get_rect().height/2

            car_center = (int(self.AI_car.x+car_width),int(self.AI_car.y+car_height))

            angle_of_line = -self.AI_car.angle_facing-angle
            
            line_start = (car_center)
            line_end = (int(max_line_length * math.cos(angle_of_line)  +  car_center[0]),
                        int(max_line_length * math.sin(angle_of_line)  +  car_center[1]))
            
            
            point = self.check_line_intersection(self.map.TRACK_BORDER,line_start,line_end)
            
            
            if point != None:
                self.distances[i] = int(math.hypot(line_start[0]-point[0],line_start[1]-point[1]))
                pygame.draw.line(self.WIN,(0,0,255),line_start,point,4)
            else:
                pygame.draw.line(self.WIN,(0,0,255),line_start,line_end,4)



    def draw(self,win, images, player_car):
        
        for img, pos in images:
            win.blit(img, pos)

        
        for i,checkpoint in enumerate(self.checkpoints):
            if self.unpassed_checkpoints[i]:
                pygame.draw.line(win,(0,255,0),checkpoint[0],checkpoint[1],2)

        
        self.detect_lines()

        player_car.draw(win)

        self.screen.blit(self.WIN, (0, 0))

        pygame.display.update()



    def collide_line(self, line, x=0, y=0):
        car_mask = pygame.mask.from_surface(line)
        offset = (int(self.x - x), int(self.y - y))
        poi = self.map.TRACK_BORDER_MASK.overlap(car_mask, offset)
        return poi



    def boost_player(self,car):
        car.max_vel = 10
        car.acceleration = 0.5
        car.move_forward()
        car.max_vel = 5
        car.acceleration = 0.1
        self.shake_screen()
        car.img = car.boosting_img



    def move_player(self,AI_car,actions):
        if actions[LEFT]:
            AI_car.rotate(left=True)
        if actions[RIGHT]:
            AI_car.rotate(right=True)
        if actions[BOOST]:
            self.boost_player(car=AI_car)
        else:
            AI_car.img = self.map.CAR
            if actions[FORWARD]:
                AI_car.move_forward()
            else:
                
                pass

        if actions [BACKWARD]:
            AI_car.move_backward()

        moved = actions[BOOST] or actions[FORWARD] or actions[BACKWARD]
        if not moved:
            AI_car.update_position()



    def reset(self):
        self.AI_car.reset()
        self.unpassed_checkpoints = [True] * len(self.checkpoints)
        self.score = 0
        self.num_frames = 0



    
    def get_state(self):
        
        return list(map(lambda x : 40/x if x != 0 else 60,self.distances)) \
                 + ([(self.AI_car.x/self.map.WIDTH),(self.AI_car.y/self.map.HEIGHT),
                     (self.AI_car.angle_facing / (2*math.pi)), 
                     (self.AI_car.angle_headed / (2*math.pi)),
                     (self.AI_car.current_speed / 10)])
   


    def calculate_reward(self):
        reward = -0.1
        done = False

        
        passed_checkpoint = self.passed_checkpoints()
        if passed_checkpoint:
            self.score += 1
            reward = 50
        
        
        min_distance = 30
        if any(distance < min_distance for distance in self.distances):
            reward -= 10

        
        if self.num_frames > self.score*50 + 500:
            reward = -200
            done = True
            
        
        if self.AI_car.collide(self.map.TRACK_BORDER_MASK) != None:
            reward = -100
            done = True

        return reward,done



    
    def play_step(self,action):
        
        self.move_player(self.AI_car,action)
        reward,done = self.calculate_reward()

        
        finish_poi_collide = self.AI_car.collide(self.map.FINISH_MASK, * self.map.FINISH_POSITION)
        if finish_poi_collide != None:
            if  not self.passing_finish_line:

                
                if finish_poi_collide[0] == 0:
                    self.AI_car.bounce()

                
                else:
                    self.passing_finish_line = True
                    self.unpassed_checkpoints = [True] * len(self.checkpoints)
                    reward = 1000
        else:
            self.passing_finish_line = False

        self.num_frames +=1
        self.clock.tick(self.FPS)
        self.draw(self.WIN, self.map.IMAGES, self.AI_car)
        return reward, done, self.score
        


if __name__ == '__main__':

    game = GameAI(FPS=60,map=Map_1)
    commands = [pygame.K_LEFT,pygame.K_RIGHT,pygame.K_UP,pygame.K_SPACE,pygame.K_DOWN,0]
    run = True

    while run:

        keys = pygame.key.get_pressed()
        action = [0,0,0,0,0,0]
        for i in range(len(action)):
            if keys[commands[i]]:
                action[i] = 1
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        reward, done, score = game.play_step(action)
        
        
