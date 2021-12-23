import pygame
import os
import sys


WIDTH = 300
HEIGHT = 600
GRAVITY = 300
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


player_image = load_image('hero.png')
block_image = load_image('block.png')


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, jump_speed=300):
        super(Player, self).__init__(player_group, all_sprites)
        self.image = player_image
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.pos = self.x, self.y = pos
        self.rect = self.image.get_rect().move(self.x, self.y)

        self.push_phase = 0
        self.in_pushing = False
        self.push_speed = 500
        self.push_dist = 80
        self.push_acc = self.push_speed ** 2 / (2 * self.push_dist) * -1

        self.jump_speed = jump_speed
        self.is_jump = True
        self.jump_phase = 0

        self.death = True
        self.move_pos = list(pos)

    def update(self, push, time):
        super(self).update(time)
        self.push_phase += time
        self.jump_phase += time
        if push and not self.death:
            self.push_phase = 0
            self.in_pushing = True
            self.move_pos[0] = self.pos[0]
        platform = pygame.sprite.spritecollideany(self, blocks_group)
        if platform and pygame.sprite.collide_mask(self, platform):
            if (self.pos[1] - platform.rect.top <= 10 or
                    platform.rect.left < self.rect.left <
                    platform.rect.right - self.rect.width):
                self.is_jump = False
                self.jump_phase = 0
                self.move_pos[1] = platform.rect.topleft[1]
                # if not self.is_playing() and self.prev_name != "landing":
                #     if self.on_map():
                #         self.start_anim("landing", 0.01)
                #     self.landing_sound.play()
                #     self.is_jump = True
            elif self.rect.right > platform.rect.right:
                self.pos[0] += 2
            elif self.rect.left < platform.rect.left:
                self.pos[0] -= 2
                self.in_pushing = False

        if self.is_jump:
            # if not self.is_playing() and self.prev_name != "jump":
            #     self.start_anim("jump", 0.15)

            self.pos[1] = (self.move_pos[1] - self.jump_speed * self.jump_phase +
                           (GRAVITY * self.jump_phase ** 2) / 2)

    update(0, )


class Blocks(pygame.sprite.Sprite):
    def __init__(self, pos=(90, HEIGHT - 50)):
        super(Blocks, self).__init__(blocks_group, all_sprites)
        self.x, self.y = pos
        self.image = block_image
        self.rect = self.image.get_rect().move(self.x, self.y)



start_screen()
player = Player((100, HEIGHT - 90))
block = Blocks()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(pygame.Color('white'))
    player_group.draw(screen)
    blocks_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
terminate()
