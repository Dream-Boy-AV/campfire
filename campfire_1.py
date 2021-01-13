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
save = [line.rstrip('\n') for line in open('save_data.txt', 'r').readlines()]
chip_names = ['blue', 'green', 'red', 'yellow']


def game():
    level_init()
    while True:
        # TODO: Define a movement availability checking function!
        # TODO: Define a chip shuffling function!
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # TODO: Add function for MOUSEBUTTONDOWN!
            ## TODO: For buttons to define respective functions, for chips to define choose function!
            ### TODO: Add chip movement function with movements limitation!
        # TODO: Add match checking function!
        # TODO: Add movement cancel and matching functions!
        # TODO: Add mission progress function!
        # TODO: Winning and losing functions!
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

    gamemode = int(save[0][7:]) % 2
    if gamemode == 1:
        cell_image = pygame.transform.scale(load_image('textures\\cell_opened.png'), (77, 77))
    else:
        cell_image = pygame.transform.scale(load_image('textures\\cell_closed.png'), (77, 77))
    cells_init(level, cell_image)

    chip_set(level)

    font = pygame.font.SysFont('impact', 42)
    label = font.render('Mission', 1, pygame.Color('#F9F9E8'))
    screen.blit(label, ((210 - label.get_rect().width) // 2 + 114, 130))

    goal = 'icons\\chip_{}.png'.format(random.choice(chip_names)) if gamemode == 1 else 'textures\\cell_closed.png'
    goal_image = pygame.transform.scale(load_image(goal), (77, 77))
    screen.blit(goal_image, ((210 - goal_image.get_rect().width) // 2 + 114, 180))

    count_text = '0/50' if gamemode == 1 else '0/{}'.format(str(cell_count))
    counter = font.render(count_text, 1, pygame.Color('#F9F9E8'))
    screen.blit(counter, ((210 - counter.get_rect().width) // 2 + 114, 260))

    timer = font.render('03:00', 1, pygame.Color('#F9F9E8'))
    screen.blit(timer, ((210 - timer.get_rect().width) // 2 + 114, 350))


def cells_init(level, cell_image):
    global cell_count
    cell_count = 0
    cells = pygame.sprite.Group()
    y = 62
    for line in level:
        x = 451
        for place in line:
            if place == '1':
                cell = pygame.sprite.Sprite(cells)
                cell.image = cell_image
                cell.rect = cell.image.get_rect()
                cell.rect.x, cell.rect.y = x, y
                cell_count += 1
            x += 81
        y += 81
    cells.draw(screen)


def chip_set(level):
    chips = pygame.sprite.Group()
    chip_list = []
    ln = 0
    y = 71
    for line in level:
        x = 460
        list_line = []
        pl = 0
        for place in line:
            if place == '1':
                chip_image = random.choice(chip_names)
                if pl > 1 and ln > 1:
                    cond1 = list_line[pl - 2] == chip_image
                    cond2 = list_line[pl - 1] == chip_image
                    cond3 = chip_list[ln - 2][pl] == chip_image
                    cond4 = chip_list[ln - 1][pl] == chip_image
                    while cond1 and cond2 or cond3 and cond4:
                        chip_image = random.choice(chip_names)
                        cond1 = list_line[pl - 2] == chip_image
                        cond2 = list_line[pl - 1] == chip_image
                        cond3 = chip_list[ln - 2][pl] == chip_image
                        cond4 = chip_list[ln - 1][pl] == chip_image
                elif pl > 1:
                    cond1 = list_line[pl - 2] == chip_image
                    cond2 = list_line[pl - 1] == chip_image
                    while cond1 and cond2:
                        chip_image = random.choice(chip_names)
                        cond1 = list_line[pl - 2] == chip_image
                        cond2 = list_line[pl - 1] == chip_image
                elif ln > 1:
                    cond3 = chip_list[ln - 2][pl] == chip_image
                    cond4 = chip_list[ln - 1][pl] == chip_image
                    while cond3 and cond4:
                        chip_image = random.choice(chip_names)
                        cond3 = chip_list[ln - 2][pl] == chip_image
                        cond4 = chip_list[ln - 1][pl] == chip_image
                list_line += [chip_image]
                chip_sprite = pygame.sprite.Sprite(chips)
                chip_sprite.image = \
                    pygame.transform.scale(load_image('icons\\chip_{}.png'.format(chip_image)),
                                           (60, 60))
                chip_sprite.rect = chip_sprite.image.get_rect()
                chip_sprite.rect.x, chip_sprite.rect.y = x, y
            else:
                list_line += [0]
            x += 81
            pl += 1
        y += 81
        chip_list += [list_line]
        ln += 1
    chips.draw(screen)


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('campfire')
    pygame.display.set_icon(load_image('textures\\icon.png'))
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
    game()
