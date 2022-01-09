import pygame
import os
import sys
import random

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


class Camera:
    def __init__(self, field_size):
        self.dy = 0
        self.camera_phase = 0

    # Сдвинуть объект obj на смещение камеры
    def apply(self, obj, y):
        obj.rect.y += self.dy
        return obj.rect.x, obj.rect.y

    def update(self, target, time):
        self.camera_phase += time
        self.dy = self.camera_phase - (GRAVITY * self.camera_phase ** 2) / 2


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


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
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


player_image = load_image('hero2.png')
block_image = load_image('block.png')


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super(Player, self).__init__(player_group, all_sprites)
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


        self.pos[0] = self.start_pos[0] + self.move_speed * self.move_phase * horizontal_move

        self.prev_horizontal_move = horizontal_move

        platform = pygame.sprite.spritecollideany(self, blocks_group)
        if platform and pygame.sprite.collide_mask(self, platform) and self.jump_speed - GRAVITY * self.jump_phase < 0 and self.rect.bottom < platform.rect.bottom:
            self.jump_phase = 0
            self.start_pos[1] = platform.rect.top - self.rect.height - 1

        self.pos[1] = (self.start_pos[1] - self.jump_speed * self.jump_phase +
                            (GRAVITY * self.jump_phase ** 2) / 2)

        self.rect.topleft = self.pos


class Blocks(pygame.sprite.Sprite):
    def __init__(self, pos=(90, HEIGHT - 50)):
        super(Blocks, self).__init__(blocks_group, all_sprites)
        self.x, self.y = pos
        self.image = block_image
        self.rect = self.image.get_rect().move(self.x, self.y)


start_screen()
player = Player((100, HEIGHT - 90))

move = 0

block1 = Blocks()
block = Blocks((150, HEIGHT - 150))
block2 = Blocks((150, HEIGHT - 300))
block3 = Blocks((90, HEIGHT - 450))
block4 = Blocks((90, HEIGHT - 600))
camera = Camera((WIDTH, HEIGHT))




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
    if 100 < player.rect.y < 200:
        camera.update(player, time)
        for sprite in all_sprites:
            if not isinstance(sprite, Player):
                camera.apply(sprite, player.rect.y)

    player_group.update(time, move)

    screen.fill(pygame.Color('white'))
    blocks_group.draw(screen)
    player_group.draw(screen)


    pygame.display.flip()
terminate()
