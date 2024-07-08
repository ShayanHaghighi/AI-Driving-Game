from pathlib import Path
if __name__=='maps':
    from helper import scale_image
else:
    from game.helper import scale_image
import pygame


class Map():
    def __init__(self,track_img,track_mask_img,finish_img,finish_position,
                 car_img,car_boost_img=None,media_path="./"):

        self.MEDIA_PATH = Path(__file__).resolve().parent / Path(media_path)

        self.TRACK = scale_image(pygame.image.load(self.MEDIA_PATH / track_img), 1)

        self.TRACK_BORDER = scale_image(pygame.image.load(self.MEDIA_PATH / track_mask_img), 1)
        self.TRACK_BORDER_MASK = pygame.mask.from_surface(self.TRACK_BORDER)

        self.FINISH = scale_image(pygame.image.load(self.MEDIA_PATH / finish_img), 1.3)
        self.FINISH_MASK = pygame.mask.from_surface(self.FINISH)
        self.FINISH_POSITION = finish_position

        self.CAR = scale_image(pygame.image.load(self.MEDIA_PATH / car_img), 0.04)
        if car_boost_img == None:
            self.BOOST_CAR=self.NORMAL_CAR
        else:
            self.BOOST_CAR = scale_image(pygame.image.load(self.MEDIA_PATH / car_boost_img), 0.04)

        self.WIDTH, self.HEIGHT = self.TRACK.get_width(), self.TRACK.get_height()

        self.IMAGES = [(self.TRACK, (0, 0)), (self.FINISH, (self.FINISH_POSITION[0], self.FINISH_POSITION[1]))]


Map_1 = Map(media_path="../media",
            track_img="track.png",track_mask_img="track_mask.png",
            finish_img="finish.png",finish_position=(720, 650),
            car_img="car_icon.png",car_boost_img="car_icon_flame.png")