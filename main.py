import random

import pygame
import os
import sys

WIDTH = 300
HEIGHT = 600

GRAVITY = 500
INCREMENT_VELOCITY_X = 0.5
MAX_VELOCITY_X = 4
MAX_VELOCITY_Y = 20
VELOCITY_X_SLOW_DOWN = 1.05

FPS = 50


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


class Text(pygame.sprite.Sprite):
    def __init__(self, text, pos, size=20,
                 font=None, color=(0, 0, 0)):
        super().__init__(game.texts_group, game.all_sprites)
        self.pos = pos
        self.color = color
        self.size = size
        self.font = font

        self.set(text)

        self.font_type = None
        self.message = None

    def set(self, text):
        if text:
            self.font_type = pygame.font.Font('data//20652.otf', self.size)
            self.message = self.font_type.render(text, True, self.color)

            game.screen.blit(self.message, self.pos)


def start_screen():
    fon = pygame.transform.scale(load_image('start_screen.jpg'), (WIDTH, HEIGHT))
    game.screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        game.clock.tick(FPS)


def lossed_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    game.screen.blit(fon, (0, 0))
    file = open('data/record.txt')
    n = int(file.readline())
    file.close()
    f = open('data/record.txt', 'w')
    f.write(str(max(int(game.score), n)))
    f.close()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        game_over = Text('GAME OVER', (50, 150), size=50)
        text = Text('score: ' + str(int(game.score)), (50, 250), size=50)
        text2 = Text('record: ' + str(max(int(game.score), n)), (50, 290), size=50)
        pygame.display.flip()
        game.clock.tick(FPS)


class Camera:
    def __init__(self, target=None, limit=500):
        self.y = 0
        self.target = target
        self.limit = limit

    def set_target(self, target, limit):
        self.target = target
        self.limit = limit

    def apply(self, group):
        for sprite in group:
            if sprite != self.target:
                sprite.rect.y = sprite.pos[1] + self.y

    def set_position(self, pos):
        if pos[1] + self.y <= self.limit:
            self.y = self.limit - pos[1]

        self.target.rect.y = pos[1] + self.y

        self.target.rect.x = pos[0]


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(game.player_group, game.all_sprites)

        self.is_alive = True

        self.image = player_image
        self.pos = self.x, self.y = list(pos)
        self.y2 = self.y
        self.rect = self.image.get_rect().move(self.x, self.y)

        self.move_phase = 0
        self.move_speed = 200

        self.jump_phase = 0
        self.jump_speed = 450
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

        self.pos[0] = (self.start_pos[0] + self.move_speed *
                       self.move_phase * horizontal_move) % 300

        self.prev_horizontal_move = horizontal_move

        platform = pygame.sprite.spritecollideany(self, game.blocks_group)
        if platform and pygame.sprite.collide_mask(self, platform) and \
                self.jump_speed - GRAVITY * self.jump_phase < 0 and \
                self.rect.bottom < platform.rect.bottom:
            self.jump_phase = 0
            self.start_pos[1] = platform.pos[1] - self.rect.height - 1

        self.pos[1] = (self.start_pos[1] - self.jump_speed * self.jump_phase +
                       (GRAVITY * self.jump_phase ** 2) / 2)

        game.cam.set_position(self.pos)


class Block(pygame.sprite.Sprite):
    def __init__(self, pos=(90, HEIGHT - 55)):
        super().__init__(game.blocks_group, game.all_sprites)
        self.pos = pos
        self.x, self.y = pos
        self.image = block_image
        self.rect = self.image.get_rect().move(self.x, self.y)


class Game:
    def __init__(self):
        self.is_running = True
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.player = None
        self.cam = None
        self.last_block = self.last_y = self.last_killed_block = None
        self.text = None
        self.score = 0
        self.flag_loss = True

        self.all_sprites = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.blocks_group = pygame.sprite.Group()
        self.texts_group = pygame.sprite.Group()

    def restart_game(self):
        for sprite in self.all_sprites.sprites():
            sprite.kill()

        self.cam = Camera()

        self.flag_loss = True

        self.player = Player((100, HEIGHT - 90))
        self.cam.set_target(self.player, 100)
        self.score = 0


        Block()
        Block((150, HEIGHT - 150))
        Block((150, HEIGHT - 300))
        Block((60, HEIGHT - 450))
        Block((90, HEIGHT - 600))
        Block((30, -100))
        Block((50, -200))
        Block((180, -350))
        self.last_block = Block((90, -500))
        Block((70, -601))
        self.last_y = -601
        self.last_killed_block = HEIGHT - 90

    def start(self):
        move = 0

        while self.is_running:
            if not self.flag_loss:
                lossed_screen()

            time = self.clock.tick() / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                if event.type == pygame.KEYDOWN:
                    if not self.player.is_alive:
                        lossed_screen()
                        self.flag_loss = True
                        self.restart_game()

                    if event.key == pygame.K_LEFT:
                        move = -1
                    if event.key == pygame.K_RIGHT:
                        move = 1
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        move = 0
                    if event.key == pygame.K_RIGHT:
                        move = 0

            if self.player.pos[1] > self.last_killed_block:
                self.player.kill()
                self.player.is_alive = False

            self.player_group.update(time, move)

            self.texts_group.update()

            self.cam.apply(self.blocks_group)

            if abs(self.last_y - self.player.pos[1]) > 600:
                self.last_y -= random.randint(50, 150)
                Block((random.randint(5, 300 - 70), self.last_y))

            for block in self.blocks_group:
                if self.player.pos[1] < 0:
                    if self.player.pos[1] - block.pos[1] <= -500:
                        last_killed_block = block.pos[1]
                        block.kill()

            self.screen.fill(pygame.Color('white'))

            self.screen.blit(background, (0, 0))

            self.blocks_group.draw(self.screen)
            self.player_group.draw(self.screen)
            self.score = max(self.score, abs((self.player.pos[1] - HEIGHT + 90)) // 100)
            self.text = Text('Score: ' + str(int(self.score)), (10, 550))

            pygame.display.flip()


pygame.init()
game = Game()

player_image = load_image('hero2.png')
block_image = load_image('block.png')
background = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))

game.restart_game()

start_screen()
game.start()

terminate()
