import pygame
import random
import math
import time
if __name__=='__main__':
    from maps import Map_1
    from car import AbstractCar
else:
    from game.maps import Map_1
    from game.car import AbstractCar

 
LEFT,RIGHT,FORWARD,BOOST,BACKWARD = 0,1,2,3,4


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

        # a list start/end coords of checkpoints
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
        
        # a list of distances in 8 directions around the car to the nearest wall
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

    # returns the point a line intersects with an image (if exists) 
    def check_line_intersection(self,image, start, end, offset=(0,0)):
            x1, y1 = start
            x2, y2 = end

            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1
            err = dx - dy

            while x1 != x2 or y1 != y2:
                # Check if the current pixel is within the image boundaries
                if 0 <= x1-offset[0] < image.get_width() and 0 <= y1-offset[1] < image.get_height():
                    pixel_alpha = image.get_at((int(x1-offset[0]), int(y1-offset[1])))[3]   # Alpha value (transparency)
                    if pixel_alpha > 0:
                        return (x1,y1)

                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x1 += sx
                if e2 < dx:
                    err += dx
                    y1 += sy

            #return intersection_points



    # checks if a checkpoint has been passed in most recent frame
    def passed_checkpoints(self):
        for i,checkpoint in enumerate(self.checkpoints):
            if (self.check_line_intersection(self.AI_car.img,checkpoint[0],checkpoint[1],(self.AI_car.x,self.AI_car.y))) != None:
                if self.unpassed_checkpoints[i]:
                    self.unpassed_checkpoints[i] = False
                    return True


    # draws the 8 lines and calculates distance to nearest wall in each direction
    def detect_lines(self):
        max_line_length = 400

        for i,angle in enumerate(self.line_angles):

            # calculate start 
            car_width = self.AI_car.img.get_rect().width/2
            car_height = self.AI_car.img.get_rect().height/2

            car_center = (int(self.AI_car.x+car_width),int(self.AI_car.y+car_height))

            angle_of_line = -self.AI_car.angle_facing-angle
            
            line_start = (car_center)
            line_end = (int(max_line_length * math.cos(angle_of_line)  +  car_center[0]),
                        int(max_line_length * math.sin(angle_of_line)  +  car_center[1]))
            
            # find poi between line and edge of track
            point = self.check_line_intersection(self.map.TRACK_BORDER,line_start,line_end)
            
            # check if line intersects with edge, and draw line
            if point != None:
                self.distances[i] = int(math.hypot(line_start[0]-point[0],line_start[1]-point[1]))
                pygame.draw.line(self.WIN,(0,0,255),line_start,point,4)
            else:
                self.distances[i] = max_line_length
                pygame.draw.line(self.WIN,(0,0,255),line_start,line_end,4)



    def draw(self,win, images, player_car):
        # draw all static images
        for img, pos in images:
            win.blit(img, pos)

        # draw all the green checkpoints
        for i,checkpoint in enumerate(self.checkpoints):
            if self.unpassed_checkpoints[i]:
                pygame.draw.line(win,(0,255,0),checkpoint[0],checkpoint[1],2)

        # update blue 'radar' lines
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
                # TODO: ease out of screen shake
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



    # represent the state of the board fed to the agent (as noramlised values)
    def get_state(self):
        
        return list(map(lambda x : 40/x if x != 0 else 60,self.distances)) \
                 + ([(self.AI_car.x/self.map.WIDTH),(self.AI_car.y/self.map.HEIGHT),
                     ((self.AI_car.angle_facing % math.pi*2) / (2*math.pi)), 
                     ((self.AI_car.angle_headed % math.pi*2) / (2*math.pi)),
                     (self.AI_car.current_speed / 5)])
   


    def calculate_reward(self):
        reward = -0.01
        done = False

        # reward car for going through checkpoints
        passed_checkpoint = self.passed_checkpoints()
        if passed_checkpoint:
            self.score += 1
            reward = 20

        reward += self.AI_car.current_speed
        
        # punish car for being too close to edge
        # min_distance = 30
        # if any(distance < min_distance for distance in self.distances):
        #     reward -= 10
        # min_inverse_distance = 10
        # for distance in self.distances:
        #     if distance != 0 and (-160/distance)+4 < min_inverse_distance:
        #         min_inverse_distance = (-160/distance)+4

        # reward += min_inverse_distance

        # punish car if it has been idle for too long
        if self.num_frames > self.score*50 + 500:
            reward = -50
            done = True
            
        # punish car for colliding with side of track
        if self.AI_car.collide(self.map.TRACK_BORDER_MASK) != None:
            reward = -30
            done = True

        return reward,done



    # represents what happens in a single frame
    def play_step(self,action):
        
        self.move_player(self.AI_car,action)
        reward,done = self.calculate_reward()

        # check overlap between car and finish line
        finish_poi_collide = self.AI_car.collide(self.map.FINISH_MASK, * self.map.FINISH_POSITION)
        if finish_poi_collide != None:
            if  not self.passing_finish_line:

                # check if passing finish line from incorrect side
                if finish_poi_collide[0] == 0:
                    self.AI_car.bounce()

                # else car has correctly passed finish line
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
    ctr = 0
    game = GameAI(FPS=60,map=Map_1)
    commands = [pygame.K_LEFT,pygame.K_RIGHT,pygame.K_UP,pygame.K_SPACE,pygame.K_DOWN,0]
    run = True

    while run:
        ctr+=1
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
        # if ctr % 60==1:
        #     print(reward)
        if done:
            game.reset()
