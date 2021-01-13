import os
import sys
import copy
import random
import pygame
from pygame.locals import *


def load_image(name):
    fullname = os.path.join('graphics', name)
    image = pygame.image.load(fullname)
    return image


FPS = 50
SIZE = WIDTH, HEIGHT = 1366, 768
SCREEN = pygame.display.set_mode(SIZE)
DISPLAY_SURFACE = pygame.display.set_mode(SIZE, DOUBLEBUF)
save = [line.rstrip('\n') for line in open('save_data.txt', 'r').readlines()]
chip_names = ['blue', 'green', 'red', 'yellow']
BLANK = pygame.transform.scale(load_image('effects\\blank.png'), (70, 70))


class Chip:
    def __init__(self, name, coords, group):
        self.name = name
        self.size = self.width, self.height = 60, 60
        self.x, self.y = coords
        self.group = group

        self.sprite_def()
        self.chosen = False

    def sprite_def(self):
        self.image = pygame.transform.scale(load_image('icons\\chip_{}.png'.format(self.name)),
                                            (self.width, self.height))
        self.sprite = pygame.sprite.Sprite(self.group)
        self.sprite.image = self.image
        self.sprite.rect = self.sprite.image.get_rect()
        self.sprite.rect.x, self.sprite.rect.y = self.x, self.y

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name

    def choose(self):
        if self.chosen:
            self.width += 4
            self.height += 4
            self.x -= 2
            self.y -= 2
        else:
            self.width -= 4
            self.height -= 4
            self.x += 2
            self.y += 2
        self.sprite_def()
        self.chosen = not self.chosen

    def ischosen(self):
        return self.chosen

    def move(self, x, y):
        self.sprite.rect.x, self.sprite.rect.y = x, y

    def disappear(self):
        self.sprite.image = BLANK

    def appear(self):
        self.sprite.image = self.image

    def set_group(self, group):
        self.group = group
        self.sprite_def()


def game():
    global chips
    level_init()
    dx, dy = 0, 0
    chosen_chip = None
    while True:
        # TODO: Define a movement availability checking function!
        # TODO: Define a chip shuffling function!
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                ev_x, ev_y = event.pos
                if pause.rect.x < ev_x < pause.rect.x + pause.rect.width \
                        and pause.rect.y < ev_y < pause.rect.y + pause.rect.height:
                    pause_func()
                elif hint.rect.x < ev_x < hint.rect.x + pause.rect.width \
                        and hint.rect.y < ev_y < hint.rect.y + pause.rect.height:
                    hint_func()
                else:
                    for chip in chips_list:
                        if chip.sprite.rect.x < ev_x < chip.sprite.rect.x + chip.sprite.rect.width \
                                and chip.sprite.rect.y < ev_y < chip.sprite.rect.y \
                                        + chip.sprite.rect.height:
                            chip.choose()
                            if chip.ischosen():
                                chosen_chip = copy.copy(chip)
                                dx, dy = event.pos[0] - chip.sprite.rect.x, \
                                         event.pos[1] - chip.sprite.rect.y
                                chip.disappear()
                            else:
                                chosen_chip = None
                            break
            if event.type == pygame.MOUSEMOTION and chosen_chip:
                x, y = event.pos
                x, y = x - dx, y - dy
                chosen_chip.move(x, y)
                chips.draw(DISPLAY_SURFACE)
            if event.type == pygame.MOUSEBUTTONUP and chosen_chip:
                ev_x, ev_y = event.pos
                chosen_chip.choose()
                for chip in chips_list:
                    if chip.sprite.rect.x < ev_x < chip.sprite.rect.x + chip.sprite.rect.width \
                            and chip.sprite.rect.y < ev_y < chip.sprite.rect.y \
                                    + chip.sprite.rect.height:
                        chip.disappear()
                        chip.sprite.rect, chosen_chip.sprite.rect = chosen_chip.sprite.rect, \
                                                                    chip.sprite.rect
                        chosen_chip.appear()
                        chip.appear()
                chosen_chip = None

            # TODO: For chips to define choose function!
            # TODO: Add chip movement function with movements limitation!
        # TODO: Add match checking function!
        # TODO: Add movement cancel and matching functions!
        # TODO: Add mission progress function!
        # TODO: Add timer running function!
        # TODO: Winning and losing functions!
        pygame.display.flip()
        clock.tick(FPS)


def level_init():
    global hint, pause
    bcg = pygame.transform.scale(load_image('textures\\level_bcg.jpg'), SIZE)
    SCREEN.blit(bcg, (0, 0))

    mission_screen = pygame.transform.scale(load_image('textures\\mission_bcg.png'), (201, 422))
    SCREEN.blit(mission_screen, (114, 51))

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
    buttons.draw(SCREEN)

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
    SCREEN.blit(label, ((210 - label.get_rect().width) // 2 + 114, 130))

    goal = 'icons\\chip_{}.png'.format(random.choice(chip_names)) if gamemode == 1 \
        else 'textures\\cell_closed.png'
    goal_image = pygame.transform.scale(load_image(goal), (77, 77))
    SCREEN.blit(goal_image, ((210 - goal_image.get_rect().width) // 2 + 114, 180))

    count_text = '0/50' if gamemode == 1 else '0/{}'.format(str(cell_count))
    counter = font.render(count_text, 1, pygame.Color('#F9F9E8'))
    SCREEN.blit(counter, ((210 - counter.get_rect().width) // 2 + 114, 260))

    timer = font.render('03:00', 1, pygame.Color('#F9F9E8'))
    SCREEN.blit(timer, ((210 - timer.get_rect().width) // 2 + 114, 350))


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
    cells.draw(SCREEN)


def chip_set(level):
    global chips_list, chips
    chips_list = []
    chips = pygame.sprite.Group()
    chip_name_list = []
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
                    cond3 = chip_name_list[ln - 2][pl] == chip_image
                    cond4 = chip_name_list[ln - 1][pl] == chip_image
                    while cond1 and cond2 or cond3 and cond4:
                        chip_image = random.choice(chip_names)
                        cond1 = list_line[pl - 2] == chip_image
                        cond2 = list_line[pl - 1] == chip_image
                        cond3 = chip_name_list[ln - 2][pl] == chip_image
                        cond4 = chip_name_list[ln - 1][pl] == chip_image
                elif pl > 1:
                    cond1 = list_line[pl - 2] == chip_image
                    cond2 = list_line[pl - 1] == chip_image
                    while cond1 and cond2:
                        chip_image = random.choice(chip_names)
                        cond1 = list_line[pl - 2] == chip_image
                        cond2 = list_line[pl - 1] == chip_image
                elif ln > 1:
                    cond3 = chip_name_list[ln - 2][pl] == chip_image
                    cond4 = chip_name_list[ln - 1][pl] == chip_image
                    while cond3 and cond4:
                        chip_image = random.choice(chip_names)
                        cond3 = chip_name_list[ln - 2][pl] == chip_image
                        cond4 = chip_name_list[ln - 1][pl] == chip_image
                chip = Chip(chip_image, (x, y), chips)
                list_line += [str(chip)]
                chips_list += [chip]
            else:
                list_line += [0]
            x += 81
            pl += 1
        y += 81
        chip_name_list += [list_line]
        ln += 1
    chips.draw(DISPLAY_SURFACE)


def pause_func():
    # TODO: Show the pause window!
    print('pause')


def hint_func():
    # TODO: Show the hint!
    print('hint')



def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('campfire')
    pygame.display.set_icon(pygame.image.load('graphics/textures/icon.png'))
    clock = pygame.time.Clock()
    game()