import random

import pygame
import os
import sys

WIDTH = 300
HEIGHT = 600

GRAVITY = 300
INCREMENT_VELOCITY_X = 0.5
MAX_VELOCITY_X = 4
MAX_VELOCITY_Y = 20
VELOCITY_X_SLOW_DOWN = 1.05

FPS = 50

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
player = None

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
blocks_group = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(' ')
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_sound(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл звука '{fullname}' не найден")
        sys.exit()
    return pygame.mixer.Sound(fullname)


def start_screen():
    fon = pygame.transform.scale(load_image('start_screen.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def loss_screen():
    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


player_image = load_image('hero2.png')
block_image = load_image('block.png')


class Camera:
    def __init__(self, target=None, limit=500):
        self.y = 0
        self.set_target(target, limit)

    def set_target(self, target, limit):
        self.target = target
        self.limit = limit

    def apply(self, group):
        for sprite in group:
            if sprite != self.target:
                sprite.rect.y = sprite.pos[1] + self.y

    def set_position(self, pos,):
        if pos[1] <= self.limit:
            self.y = self.limit - pos[1]
            self.target.rect.y = self.limit
        else:
            self.target.rect.y = pos[1] + self.y

        self.target.rect.x = pos[0]


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(player_group, all_sprites)

        self.image = player_image
        self.pos = self.x, self.y = list(pos)
        self.y2 = self.y
        self.rect = self.image.get_rect().move(self.x, self.y)

        self.move_phase = 0
        self.move_speed = 200

        self.jump_phase = 0
        self.jump_speed = 300
        self.start_pos = list(self.rect.topleft)

        self.prev_horizontal_move = 0

    def update(self, time, horizontal_move=0):
        self.jump_phase += time
        self.move_phase += time

        if horizontal_move != self.prev_horizontal_move:
            self.start_pos[0] = self.rect.left
            self.move_phase = 0
        else:
            self.move_phase += time

        self.pos[0] = (self.start_pos[0] + self.move_speed * self.move_phase * horizontal_move) % 300

        self.prev_horizontal_move = horizontal_move

        platform = pygame.sprite.spritecollideany(self, blocks_group)
        if platform and pygame.sprite.collide_mask(self, platform) and \
                self.jump_speed - GRAVITY * self.jump_phase < 0 and \
                self.rect.bottom < platform.rect.bottom:
            self.jump_phase = 0
            self.start_pos[1] = platform.pos[1] - self.rect.height - 1

        self.pos[1] = (self.start_pos[1] - self.jump_speed * self.jump_phase +
                       (GRAVITY * self.jump_phase ** 2) / 2)

        cam.set_position(self.pos)


class Blocks(pygame.sprite.Sprite):
    def __init__(self, pos=(90, HEIGHT - 55)):
        super().__init__(blocks_group, all_sprites)
        self.pos = pos
        self.x, self.y = pos
        self.image = block_image
        self.rect = self.image.get_rect().move(self.x, self.y)



start_screen()
cam = Camera()

player = Player((100, HEIGHT - 90))
cam.set_target(player, 200)

move = 0

block1 = Blocks()
block = Blocks((150, HEIGHT - 150))
block2 = Blocks((150, HEIGHT - 300))
block3 = Blocks((90, HEIGHT - 450))
block4 = Blocks((90, HEIGHT - 600))
Blocks((90, -100))
Blocks((90, -200))
Blocks((180, -350))
last_block = Blocks((90, -500))
Blocks((90, -601))
last_y = -601
last_killed_block = HEIGHT - 90


running = True
while running:
    time = clock.tick() / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                move = -1
            if event.key == pygame.K_RIGHT:
                move = 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                move = 0
            if event.key == pygame.K_RIGHT:
                move = 0

    if player.pos[1] > last_killed_block:
        loss_screen()
        player.kill()


    player_group.update(time, move)

    cam.apply(blocks_group)

    if abs(last_y - player.pos[1]) > 600:
        last_y -= random.randint(50, 150)
        Blocks((random.randint(0, 300 - 50), last_y))

    for blocks in blocks_group:
        if player.pos[1] - blocks.pos[1] <= -650:
            last_killed_block = blocks.pos[1]
            blocks.kill()

    screen.fill(pygame.Color('white'))

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    blocks_group.draw(screen)
    player_group.draw(screen)

    pygame.display.flip()

terminate()
