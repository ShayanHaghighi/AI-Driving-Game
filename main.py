import pygame
import time
import random
import math
from pathlib import Path
from helper import scale_image, blit_rotate_center

mediaPath = Path(__file__).resolve().parent / Path("./media")

TRACK = scale_image(pygame.image.load(mediaPath / "track.png"), 1)

TRACK_BORDER = scale_image(pygame.image.load(mediaPath / "track_mask.png"), 1)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = scale_image(pygame.image.load(mediaPath / "finish.png"), 1.1)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (600, 473)

NORMAL_CAR = scale_image(pygame.image.load(mediaPath / "car_icon.png"), 0.07)
FLAME_CAR = scale_image(pygame.image.load(mediaPath / "car_icon_flame.png"), 0.07)
CAR = NORMAL_CAR

images = [(TRACK, (0, 0)), (FINISH, (FINISH_POSITION[0], FINISH_POSITION[1]))]


WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()

FPS = 60


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel*math.pi/180

        self.friction = 0.8
        # represents the angle the car is headed
        self.angle_vel = 0
        # represents the angle the car is facing
        self.angle = math.pi/2
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.reversing = False

    def rotate(self, left=False, right=False):
        if left:
            self.angle = (self.angle + self.rotation_vel) % (2*math.pi)
        elif right:
            self.angle = (self.angle - self.rotation_vel) % (2*math.pi)

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), math.degrees(self.angle))

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.angle_vel = (self.angle_vel + math.pi) % (2*math.pi)
        self.angle = (self.angle + math.pi) % (2*math.pi)
        self.vel *0.5
        self.move()

    def norm_angle_vel(self):

        if self.reversing:# and round(self.angle,3) == round(self.angle_vel,3):
            return self.angle
        else:
            angle = self.angle
        if abs(self.angle - self.angle_vel) < math.pi:
            return (self.friction * self.angle_vel + (1 - self.friction) * angle) % (2*math.pi)
        elif self.angle_vel>self.angle:
            return ((self.friction * (self.angle_vel-math.pi*2) + (1 - self.friction) * (angle))) % (2*math.pi)
        else:
            return ((self.friction * (self.angle_vel+math.pi*2) + (1 - self.friction) * (angle))) % (2*math.pi)
            

    def move_forward(self):
        self.reversing = False
        # self.vel = min(self.vel + self.acceleration, self.max_vel)
        # cosine rule ->
        if self.vel > self.max_vel:
            self.vel *= 0.95
        else:
            self.vel = min(
                math.sqrt(
                    ((self.vel) ** 2)
                    + (self.acceleration**2)
                    - (
                        2
                        * (self.vel)
                        * self.acceleration
                        * math.cos(
                            math.pi + (self.norm_angle_vel() - self.angle)
                        )
                    )
                ),
                self.max_vel,
            )
        self.move()

    def move_backward(self):
        self.reversing = True
        self.vel = max(self.vel-self.acceleration*2,-self.max_vel/2)
        # self.vel = min(
        #         math.sqrt(
        #             ((self.vel) ** 2)
        #             + (self.acceleration**2)
        #             - (
        #                 2
        #                 * (self.vel)
        #                 * self.acceleration
        #                 * math.cos(
        #                     math.pi + (self.norm_angle_vel() - (self.angle-math.pi))
        #                 )
        #             )
        #         ),
        #         self.max_vel,
        #     )
        self.move()

    def move(self):
        # sin rule ->
        if self.vel == 0:
            self.angle_vel = 0
        else:
            #print(f"angle_vel:{self.angle_vel},angle:{self.angle},vel:{self.vel},acc:{self.acceleration},maxVel:{self.max_vel}")
            # if self.reversing:
            #     angle = (self.angle - math.pi) % (2*math.pi)
            # else:
            angle = self.angle
            if 0 < self.vel < 0.1*self.acceleration*10:
                temp = 1
            elif -0.1*self.acceleration*10 < self.vel < 0:
                temp = 1
            else:
                temp = (
                    math.sin(
                                self.norm_angle_vel() + math.pi - (angle)
                            )
                            * self.acceleration
                    ) / self.vel
            self.angle_vel = (self.norm_angle_vel() + (math.asin(temp))) % (2*math.pi)

        vertical = math.cos((self.angle_vel)) * self.vel
        horizontal = math.sin((self.angle_vel)) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = math.pi/2
        self.vel = 0
        self.angle_vel = 0


class PlayerCar(AbstractCar):
    IMG = CAR
    START_POS = (550, 500)

class GameAI:


    def __init__(self):    
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.WIN = pygame.Surface((WIDTH, HEIGHT))

        pygame.display.set_caption("Racing Game!")

        self.clock = pygame.time.Clock()

        # parameters: max_vel, rotation_vel
        self.AI_car = PlayerCar(5, 7)
        self.passing = False
        self.passingCheckpoints = False
        self.checkpoints = [((400,460),(400,585)),((200,460),(200,590)),((167,444),(23,500))
                            ,((300,460),(300,585)),((450,460),(450,585))#,((350,460),(350,585))
                            ,((167,435),(36,351)),((173,438),(169,313)),((251,318),(300,438))
                            ,((276,316),(439,400)),((276,316),(370,202)),((212,310),(250,170))
                            ,((154,163),(88,300)),((141,154),(16,157)),((156,139),(117,21))
                            ,((320,160),(364,22)),((450,184),(579,157)),((600,250),(525,353))
                            ,((633,254),(741,300)),((750,150),(750,45)),((800,212),(960,212))
                            ,((841,277),(950,277)),((871,333),(938,333)),((791,443),(973,443))
                            ,((711,466),(781,589)),((500,460),(500,585)),((167,435),(120,315))
                            ,((240,438),(220,313)),((417,176),(504,38)),((230,154),(290,20))
                            ,((486,268),(593,219))
                            ]
        self.distances = [0,0,0,0,0,0,0,0]
        self.validCheckpoints = [1] * len(self.checkpoints)
        self.score = 0
        self.num_steps = 0

        



    def shake_screen(self):
        xOffset = random.randint(-1, 1)
        yOffset = random.randint(-1, 1)
        self.screen.blit(self.WIN, (xOffset, yOffset))

        pygame.display.update()

    def draw_line(self,image, start, end, offset=(0,0)):
            intersection_points = []
            x1, y1 = start
            x2, y2 = end

            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1
            err = dx - dy

            last_was_intersection = False

            while x1 != x2 or y1 != y2:
                # Check if the current pixel is within the image boundaries
                if 0 <= x1-offset[0] < image.get_width() and 0 <= y1-offset[1] < image.get_height():
                    pixel_alpha = image.get_at((int(x1-offset[0]), int(y1-offset[1])))[3]   # Alpha value (transparency)
                    if pixel_alpha > 0:
                        return (x1,y1)
                        # Non-transparent pixel, record intersection point or perform other actions
                        if not last_was_intersection:
                            intersection_points.append((x1, y1))
                            last_was_intersection = True
                    else:
                        last_was_intersection = False


                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x1 += sx
                if e2 < dx:
                    err += dx
                    y1 += sy

            #return intersection_points


    def passed_checkpoints(self):
        passingAny = False
        for i,checkpoint in enumerate(self.checkpoints):
            if (poi := self.draw_line(self.AI_car.img,checkpoint[0],checkpoint[1],(self.AI_car.x,self.AI_car.y))) != None:
                passingAny = True
                if not self.passingCheckpoints and self.validCheckpoints[i]==1:

                    self.validCheckpoints[i] = 0
                    self.passingCheckpoints = True
                    return True
        if not passingAny:
            self.passingCheckpoints = False  


 
    def detect_lines(self):
        angles = [0,math.pi/4,math.pi/2,3*math.pi/4,math.pi,5*math.pi/4,3*math.pi/2,7*math.pi/4]
        lenLine = 1000

        for i,angle in enumerate(angles):
            line_start = (int(self.AI_car.x+12.5),int(self.AI_car.y+25))
            line_end = (int(lenLine*math.cos((-self.AI_car.angle-angle))+self.AI_car.x+12.5),int(lenLine*math.sin((-self.AI_car.angle-angle))+self.AI_car.y+25))
            point = self.draw_line(TRACK_BORDER,line_start,line_end)
            # for collision in points:
            if point != None:
                #print(math.hypot(line_start[0]-point[0],line_start[1]-point[1]))
                self.distances[i] = int(math.hypot(line_start[0]-point[0],line_start[1]-point[1]))
                pygame.draw.line(self.WIN,(0,0,255),line_start,point,4)
            else:
                
                pygame.draw.line(self.WIN,(0,0,255),line_start,line_end,4)



    def draw(self,win, images, player_car):
        # draw all static images
        for img, pos in images:
            win.blit(img, pos)

        for i,checkpoint in enumerate(self.checkpoints):
            if self.validCheckpoints[i] == 1:
                pygame.draw.line(win,(0,255,0),checkpoint[0],checkpoint[1],2)


        #-------line logic-----------
        self.detect_lines()




        # draw player car
        player_car.draw(win)

        self.screen.blit(self.WIN, (0, 0))

        pygame.display.update()


    def collide_line(self, line, x=0, y=0):
        car_mask = pygame.mask.from_surface(line)
        offset = (int(self.x - x), int(self.y - y))
        poi = TRACK_BORDER_MASK.overlap(car_mask, offset)
        return poi


    def move_player(self,AI_car,actions):
        global CAR
        moved = False
        #[left, right, accel, boost, left+accel, right+accel, left+boost, right+boost, nothing]

        if actions[0]==1:
            AI_car.rotate(left=True)
        if actions[1]==1:
            AI_car.rotate(right=True)
       
        #boost
        if actions[3]==1:
            AI_car.max_vel = 10
            AI_car.acceleration = 0.5
            moved = True
            AI_car.move_forward()
            self.shake_screen()
            AI_car.img = FLAME_CAR
        else:
            AI_car.img = NORMAL_CAR
            self.screen.blit(self.WIN, (0, 0))
            pygame.display.update()
            if actions[2]==1:
                AI_car.max_vel = 5
                AI_car.acceleration = 0.1
                moved = True
                AI_car.move_forward()
            else:
                # TODO: ease out of screen shake
                pass
        if actions [4]==1:
            #AI_car.vel *= 0.8
            AI_car.move_backward()
            moved = True
        if not moved:
            AI_car.reduce_speed()


    def reset(self):
        self.AI_car.reset()
        self.validCheckpoints = [1] * len(self.checkpoints)
        self.score = 0
        self.num_steps = 0

    
    def get_state(self):
        
        state = list(map(lambda x : (x/600),self.distances)) + ([(self.AI_car.x/600),(self.AI_car.y/600),(self.AI_car.angle/(2*math.pi)),(self.AI_car.angle_vel/(2*math.pi)),(self.AI_car.vel/10)])
        #print(state)
        return state



    #------------------starting and running the game---------------------------


    def play_step(self,action):
        done = False
        reward = -0.1
        self.num_steps +=1
        #print(self.distances)
        
        passed = self.passed_checkpoints()

        self.move_player(self.AI_car,action)
        
        # if action[2]==1 or action[3]==1:
        #     reward += 1

        # min_distance = 40
        # if self.distances[1] < min_distance or self.distances[2] < min_distance or self.distances[3] < min_distance:
        #     reward -= 2


        if passed:
            self.score += 1

            #print("passing gate")
            reward = 20
        
        # if(abs(self.distances[0]-self.distances[4])<20 and (min(self.distances)==self.distances[0] or min(self.distances)==self.distances[4])):
        #     reward += 1


        # if self.AI_car.vel==0:
        #     reward -= 0.5

        if self.num_steps > self.score*200 + 200:
            done = True
            reward = -50
            
        if self.AI_car.collide(TRACK_BORDER_MASK) != None:
            reward = -10
            done = True
            #self.reset()

        finish_poi_collide = self.AI_car.collide(FINISH_MASK, *FINISH_POSITION)
        if finish_poi_collide != None:
                if(not self.passing):
                    if finish_poi_collide[0] == 0:
                        self.AI_car.bounce()
                    else:
                        #self.AI_car.reset()
                        self.passing = True
                        self.validCheckpoints = [1] * len(self.checkpoints)
                        reward = 1000
        else:
            self.passing = False

        
        self.clock.tick(FPS)
        self.draw(self.WIN, images, self.AI_car)
        return reward, done, self.score
        

    #--------------------------end of running game
        

if __name__ == '__main__':
    game = GameAI()


    while True:
        keys = pygame.key.get_pressed()
        action = [0,0,0,0,0,0]
        if keys[pygame.K_LEFT]:
            action[0] = 1
        elif keys[pygame.K_RIGHT]:
            action[1] = 1

        if keys[pygame.K_UP]:
            action[2] = 1

        
        if keys[pygame.K_SPACE]:
            action[3] = 1
        if keys[pygame.K_DOWN]:
            action[4] = 1
        run = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        reward, done, score = game.play_step(action)

        if not run:
            break
