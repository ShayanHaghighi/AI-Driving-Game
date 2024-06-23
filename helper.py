import matplotlib.pyplot as plt
from IPython import display
import pygame

plt.ion()

def plot(scores, mean_scores):
    display.clear_output(wait=True)
    # display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    _=plt.plot(scores)
    _=plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)

def close():
    plt.close()

def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)

def print_click_coordinates(event):
    global ctr
    if event.type == pygame.MOUSEBUTTONDOWN:
        x, y = event.pos
        if ctr % 2 == 0:
            print(f"(({x}, {y}),",end='')
        else:
            print(f"({x}, {y})),")
        ctr +=1