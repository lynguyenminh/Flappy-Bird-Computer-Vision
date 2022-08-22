import pygame, random, time
from pygame.locals import *
from sign_cv import handle_sign
import sign_cv
import threading
from threading import Thread
import ctypes
import json


from object_game import Bird, Ground, Pipe


f = open('config.json')
data = json.load(f)
f.close()

#VARIABLES
SCREEN_WIDHT = data.get('SCREEN_WIDHT')
SCREEN_HEIGHT = data.get('SCREEN_HEIGHT')
SPEED = data.get('SPEED') # speed bird
GRAVITY = data.get('GRAVITY')
GAME_SPEED = data.get('GAME_SPEED') # speed race

GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT= data.get('GROUND_HEIGHT')

PIPE_WIDHT = data.get('PIPE_WIDHT')
PIPE_HEIGHT = data.get('PIPE_HEIGHT')

PIPE_GAP = data.get('PIPE_GAP')

status = False # sign from pose
begin = True # sign from game

wing = 'assets/audio/wing.wav'
hit = 'assets/audio/hit.wav'


def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])


def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted


def start_game():
    global begin
    while begin:
        clock.tick(15)

        # flapping wings to start game
        if status:
            bird.bump()
            pygame.mixer.music.load(wing)
            pygame.mixer.music.play()
            begin = False

        screen.blit(BACKGROUND, (0, 0))
        screen.blit(BEGIN_IMAGE, (120, 150))

        if is_off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0])

            new_ground = Ground(GROUND_WIDHT - 20)
            ground_group.add(new_ground)

        bird.begin()
        ground_group.update()

        bird_group.draw(screen)
        ground_group.draw(screen)

        pygame.display.update()


def playing_game():
    while True:
        clock.tick(15)
        # control bird       
        if status:
            bird.bump()
            pygame.mixer.music.load(wing)
            pygame.mixer.music.play()
        screen.blit(BACKGROUND, (0, 0))

        if is_off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0])

            new_ground = Ground(GROUND_WIDHT - 20)
            ground_group.add(new_ground)

        if is_off_screen(pipe_group.sprites()[0]):
            pipe_group.remove(pipe_group.sprites()[0])
            pipe_group.remove(pipe_group.sprites()[0])

            pipes = get_random_pipes(SCREEN_WIDHT * 2)

            pipe_group.add(pipes[0])
            pipe_group.add(pipes[1])

        bird_group.update()
        ground_group.update()
        pipe_group.update()

        bird_group.draw(screen)
        pipe_group.draw(screen)
        ground_group.draw(screen)

        pygame.display.update()

        if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
                pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
            pygame.mixer.music.load(hit)
            pygame.mixer.music.play()
            time.sleep(1)
            break


class my_thread(Thread):
    def __init__(self, name_function):
        Thread.__init__(self)
        self.name_function = name_function

    def run(self):
        if self.name_function == 'change_flag':
            change_flag()
        elif self.name_function == 'get_event':
            get_event()

    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
  
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


def get_event():
    global status
    for i in handle_sign():
        if i:
            status = True
        else: 
            status = False


def change_flag():
    sign_cv.stop_sign = True


pygame.mixer.init()
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()

bird_group = pygame.sprite.Group()
bird = Bird()
bird_group.add(bird)

ground_group = pygame.sprite.Group()

for i in range (2):
    ground = Ground(GROUND_WIDHT * i)
    ground_group.add(ground)

pipe_group = pygame.sprite.Group()
for i in range (2):
    pipes = get_random_pipes(SCREEN_WIDHT * i + 800)
    pipe_group.add(pipes[0])
    pipe_group.add(pipes[1])


if __name__=="__main__":
    clock = pygame.time.Clock()

    # start pose detection
    t1 = my_thread('get_event')
    t1.start()

    print('FLAPPY BIRD GAME')
    print('TO START GAME, PLEASE FLAPPING WING')

    # click (flapping wings) to start game
    start_game()

    # start play game
    playing_game()

    # stop pose detect
    t2 = my_thread('change_flag')
    t2.start()


    t1.join()
    t2.join()