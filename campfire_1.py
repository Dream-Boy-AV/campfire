import os
import sys
import random
import pygame


def load_image(name):
    fullname = os.path.join('graphics', name)
    image = pygame.image.load(fullname)
    return image


FPS = 50
SIZE = WIDTH, HEIGHT = 1366, 768

def game():
    level_init()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)

def level_init():
    bcg = pygame.transform.scale(load_image('textures\\level_bcg.jpg'), SIZE)
    screen.blit(bcg, (0, 0))

    mission_screen = pygame.transform.scale(load_image('textures\\mission_bcg.png'), (201, 422))
    screen.blit(mission_screen, (114, 51))

    buttons = pygame.sprite.Group()
    hint_image = pygame.transform.scale(load_image('icons\\level_hint_btn.png'), (94, 94))
    hint = pygame.sprite.Sprite(buttons)
    hint.image = hint_image
    hint.rect = hint.image.get_rect()
    hint.rect.x = 167
    hint.rect.y = 503

    pause_image = pygame.transform.scale(load_image('icons\\level_pause_btn.png'), (94, 94))
    pause = pygame.sprite.Sprite(buttons)
    pause.image = pause_image
    pause.rect = pause.image.get_rect()
    pause.rect.x = 167
    pause.rect.y = 612
    buttons.draw(screen)

    level = open('levels/type_{}.txt'.format(str(random.randrange(8))), 'r').readlines()
    level = [line.rstrip('\n').split() for line in level]

def terminate():
    pygame.quit()
    sys.exit()



if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('campfire')
    pygame.display.set_icon(pygame.image.load('graphics/textures/icon.png'))
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
    game()
