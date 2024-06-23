
import math
from helper import blit_rotate_center
import pygame

class AbstractCar:
    
    def __init__(self, max_velocity=5, rotation_vel=7,drift=0.9,acceleration=0.1,initial_angle=math.pi/2,start_pos=(700, 704)):

        # ------------ CAR PARAMETERS -----------------------
        self.initial_angle = initial_angle
        self.drift = drift
        self.acceleration = acceleration
        self.x, self.y = start_pos
        self.rotation_vel = rotation_vel*math.pi/180
        self.max_velocity = max_velocity
        # ---------------------------------------------------

        # the image of the car
        self.img = self.IMG
        self.boosting_img = self.BOOSTING_IMG

        self.current_speed = 0
        # represents the angle the car is headed
        self.angle_headed = 0
        # represents the angle the car is facing
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

                # decrease the speed,
                self.current_speed *= 0.95
                current_acceleration = 0

            elif reversing:
                # if reversing, set the angle (of the force of the engine) to go backwards from the car
                current_angle = (self.angle_facing - math.pi)

        # a vector representing the magnitude and direction of where the car is headed
        momentum_vector = (self.angle_headed,self.current_speed)

        # a vector representing the magnitude and direction of where the engine is pushing
        engine_force_vector = (current_angle,current_acceleration)

        # new vector for (direction,speed) of car after forces are taken into account
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




