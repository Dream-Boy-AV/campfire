import pygame


if __name__ == '__main__':
    pygame.init()
    size = width, height = 1366, 768
    screen = pygame.display.set_mode(size)
    pygame.display.set_icon(pygame.image.load('graphics/textures/icon.png'))

    print('Ура!')


    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass
    pygame.quit()