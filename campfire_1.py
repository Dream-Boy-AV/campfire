import os
import sys
import random
import pygame


def load_image(name):
    # Function for more convenient image loading
    fullname = os.path.join('graphics', name)
    image = pygame.image.load(fullname)
    return image


# Initializing Pygame
pygame.init()
pygame.display.set_caption('campfire')
pygame.display.set_icon(load_image('textures\\icon.png'))

# Constants:
FPS = 50 # FPS value for animations
SIZE = WIDTH, HEIGHT = 1366, 768
MENU_BTN_SIZE = 303, 95
## Saved level and options
save = [line.rstrip('\n') for line in open('save_data.txt', 'r').readlines()]
chip_names = ['blue', 'green', 'red', 'yellow'] # Names for chips to choose from
game_on, menu = False, False # Interface determinants
SCREEN = pygame.display.set_mode(SIZE) # Basic display
DISPLAY_SURFACE = pygame.display.set_mode(SIZE) # Additional blank display
BLANK = pygame.transform.scale(load_image('effects\\blank.png'), (70, 70)) # Blank texture
clock = pygame.time.Clock()

# Initializing chip containers
chips_list = []
chips = pygame.sprite.Group()

# Initializing sound system
pygame.mixer.init()

BTN_CLICK = pygame.mixer.Sound('sounds\\effects\\button_push.mp3')
CHIP_CLICK = pygame.mixer.Sound('sounds\\effects\\chip_push.mp3')
MATCH_SND = pygame.mixer.Sound('sounds\\effects\\chip_match.mp3')
MISSION_SND = pygame.mixer.Sound('sounds\\effects\\mission_fill.mp3')
RETURN_SND = pygame.mixer.Sound('sounds\\effects\\chip_return.mp3')
START_SND = pygame.mixer.Sound('sounds\\effects\\game_start.mp3')
WIN_SND = pygame.mixer.Sound('sounds\\effects\\win.mp3')
FAIL_SND = pygame.mixer.Sound('sounds\\effects\\fail.mp3')


class Chip:
    # Special class for playable chip on field.

    def __init__(self, name, coords, group):
        self.name = name
        self.size = self.width, self.height = 60, 60
        self.x, self.y = coords
        self.original_coords = coords
        self.move_direction = None
        self.group = group

        self.image = pygame.transform.scale(load_image('icons\\chip_{}.png'.format(self.name)),
                                            (self.width, self.height))
        self.sprite_def()
        self.chosen = False

    def sprite_def(self):
        # Initializing chip sprite
        self.sprite = pygame.sprite.Sprite(self.group)
        self.sprite.image = self.image
        self.sprite.rect = self.sprite.image.get_rect()
        self.sprite.rect.x, self.sprite.rect.y = self.x, self.y

    def __eq__(self, other):
        # Method for matching comparison
        return self.name == other.name

    def __str__(self):
        # Method for convenient (debug) presentation
        return self.name

    def choose(self):
        # Method for visual choose of chip
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
        # Method to check if this chip is chosen
        return self.chosen

    def move(self, x, y):
        # Method to visually move chip
        if abs(self.original_coords[0] - x) < 81 and abs(self.original_coords[1] - y) < 81:
            if not self.move_direction:
                self.direction_def(x, y)
            elif self.move_direction == 'hor':
                self.sprite.rect.x = x
                self.x = x
            elif self.move_direction == 'ver':
                self.sprite.rect.y = y
                self.y = y

    def direction_def(self, x, y):
        # Moving left or right
        if abs(x - self.original_coords[0]) > abs(y - self.original_coords[1]):
            self.move_direction = 'hor'
        # Moving up or down
        elif abs(y - self.original_coords[1]) > abs(x - self.original_coords[0]):
            self.move_direction = 'ver'

    def replace(self, other):
        # Method to swap chips positions
        self.move_direction = None
        other.sprite.rect, self.sprite.rect = self.sprite.rect, other.sprite.rect
        (other.x, other.y), (self.x, self.y) = (self.x, self.y), (other.x, other.y)
        other.original_coords, self.original_coords = self.original_coords, other.original_coords

    def set_original_pos(self):
        # Returns chip to it's original position
        self.sprite.rect.x, self.sprite.rect.y = self.original_coords
        self.x, self.y = self.original_coords
        self.move_direction = None

    def disappear(self):
        # Method to set a transparent texture to chip simulating it's disappearance
        self.sprite.image = BLANK

    def appear(self):
        # Method to set a native texture to chip simulating it's appearance
        self.sprite.image = self.image


def game():
    global chips
    # Base game function

    # Starting game with the main menu
    main_menu()
    dx, dy = 0, 0
    chosen_chip = None
    while True:
        # TODO: Define a movement availability checking function!
        # TODO: Define a chip shuffling function!
        for event in pygame.event.get():
            # if user quits, termination function starts
            if event.type == pygame.QUIT:
                terminate()
            if menu:
                # if user is in main menu
                if event.type == pygame.MOUSEBUTTONDOWN:
                    ev_x, ev_y = event.pos
                    for btn in menu_buttons:
                        # if user clicks buttons, respective function starts
                        # TODO: Redefine to point collide check
                        if btn.rect.x < ev_x < btn.rect.x + btn.rect.width \
                                and btn.rect.y < ev_y < btn.rect.y + btn.rect.height:
                            BTN_CLICK.play()
                            # "Exit" button starts termination function
                            if btn.function == 'exit':
                                terminate()
                            else:
                                menu_func(btn.function)
            if game_on:
                # if user is playing a level
                if event.type == pygame.MOUSEBUTTONDOWN:
                    ev_x, ev_y = event.pos
                    # Button clicks start respective functions
                    # TODO: Redefine to point collide check
                    if pause.rect.x < ev_x < pause.rect.x + pause.rect.width \
                            and pause.rect.y < ev_y < pause.rect.y + pause.rect.height:
                        BTN_CLICK.play()
                        pause_func()
                    # TODO: Redefine to point collide check
                    elif hint.rect.x < ev_x < hint.rect.x + pause.rect.width \
                            and hint.rect.y < ev_y < hint.rect.y + pause.rect.height:
                        BTN_CLICK.play()
                        hint_func()
                    else:
                        # Chip click makes the chip chosen
                        for chip in chips_list:
                            if chip.sprite.rect.x < ev_x < chip.sprite.rect.x + chip.sprite.rect.width \
                                    and chip.sprite.rect.y < ev_y < chip.sprite.rect.y \
                                            + chip.sprite.rect.height:
                                chip.choose()
                                if chip.ischosen():
                                    chosen_chip = chip
                                    dx, dy = event.pos[0] - chip.sprite.rect.x, \
                                             event.pos[1] - chip.sprite.rect.y
                                else:
                                    chosen_chip = None
                                break
                if event.type == pygame.MOUSEMOTION and chosen_chip:
                    # Moving the chosen chip
                    x, y = event.pos
                    x, y = x - dx, y - dy
                    chosen_chip.move(x, y)
                    for chip in chips_list:
                        if chip.sprite.rect.x < x < chip.sprite.rect.x + chip.sprite.rect.width \
                                and chip.sprite.rect.y < y < chip.sprite.rect.y \
                                        + chip.sprite.rect.height:
                            chosen_chip.choose()
                            chosen_chip.replace(chip)
                            chosen_chip = None
                            break
                if event.type == pygame.MOUSEBUTTONUP:
                    # Canceling the unfinished move
                    if chosen_chip:
                        chosen_chip.choose()
                        chosen_chip.set_original_pos()
                    chosen_chip = None
        # TODO: Add match checking function!
        # TODO: Add movement cancel and matching functions!
        # TODO: Add mission progress function!
        # TODO: Add timer running function!
        # TODO: Winning and losing functions!

        chips.draw(DISPLAY_SURFACE)
        pygame.display.flip()
        clock.tick(FPS)


def main_menu():
    # Function for main menu initialization
    global menu, menu_buttons, song
    menu = True

    # Initializing background
    bcg = pygame.transform.scale(load_image('textures\\main_menu_bcg.jpg'), SIZE)
    SCREEN.blit(bcg, (0, 0))

    # Initializing logo
    logo = pygame.transform.scale(load_image('textures\\logo.png'), (854, 137))
    SCREEN.blit(logo, (256, 116))

    # Initializing menu buttons
    menu_buttons = pygame.sprite.Group()

    ng = pygame.sprite.Sprite(menu_buttons)
    ng.image = pygame.transform.scale(load_image('icons\\main_new_game_btn.png'), MENU_BTN_SIZE)
    ng.rect = ng.image.get_rect()
    ng.rect.x, ng.rect.y = 342, 433
    ng.function = 'ng'

    cont = pygame.sprite.Sprite(menu_buttons)
    cont.image = pygame.transform.scale(load_image('icons\\main_continue_btn.png'), MENU_BTN_SIZE)
    cont.rect = cont.image.get_rect()
    cont.rect.x, cont.rect.y = 722, 433
    cont.function = 'cont'

    hlp = pygame.sprite.Sprite(menu_buttons)
    hlp.image = pygame.transform.scale(load_image('icons\\main_help_btn.png'), MENU_BTN_SIZE)
    hlp.rect = hlp.image.get_rect()
    hlp.rect.x, hlp.rect.y = 170, 577
    hlp.function = 'help'

    opt = pygame.sprite.Sprite(menu_buttons)
    opt.image = pygame.transform.scale(load_image('icons\\main_options_btn.png'), MENU_BTN_SIZE)
    opt.rect = opt.image.get_rect()
    opt.rect.x, opt.rect.y = 532, 577
    opt.function = 'options'

    ext = pygame.sprite.Sprite(menu_buttons)
    ext.image = pygame.transform.scale(load_image('icons\\main_exit_btn.png'), MENU_BTN_SIZE)
    ext.rect = ng.image.get_rect()
    ext.rect.x, ext.rect.y = 892, 577
    ext.function = 'exit'
    menu_buttons.draw(SCREEN)

    # Initializing main menu music
    song = pygame.mixer.Sound('sounds\\songs\\menu_song.mp3')
    song.play(-1)


def level_init():
    global menu, game_on, hint, pause, song
    menu = False
    game_on = True

    # Initializing background
    bcg = pygame.transform.scale(load_image('textures\\level_bcg.jpg'), SIZE)
    SCREEN.blit(bcg, (0, 0))

    # Initializing mission screen
    mission_screen = pygame.transform.scale(load_image('textures\\mission_bcg.png'), (201, 422))
    SCREEN.blit(mission_screen, (114, 51))

    # Initializing level buttons
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

    # Initializing level field
    if save[1][6:] == 'None':
        n = random.randrange(8)
        level = open('levels/type_{}.txt'.format(str(n), 'r')).readlines()
        data = open('save_data.txt', 'r').read()
        data = data[:15] + str(n) + data[19:]
        with open('save_data.txt', 'w') as savedata:
            savedata.write(data)
    else:
        level = open('levels/type_{}.txt'.format(save[1][6:]), 'r').readlines()
    level = [line.rstrip('\n').split() for line in level]

    # Initializing game mode
    gamemode = int(save[0][7:]) % 2

    # Initializing cells
    if gamemode == 1:
        cell_image = pygame.transform.scale(load_image('textures\\cell_opened.png'), (77, 77))
    else:
        cell_image = pygame.transform.scale(load_image('textures\\cell_closed.png'), (77, 77))
    cells_init(level, cell_image)

    # Initializing chips
    chip_set(level)

    # Initializing mission info
    # Level
    font = pygame.font.SysFont('impact', 42)
    lv = font.render('Level {}'.format(save[0][7:]), 1, pygame.Color('#F9F9E8'))
    SCREEN.blit(lv, ((210 - lv.get_rect().width) // 2 + 114, 80))

    # Heading
    label = font.render('Mission', 1, pygame.Color('#F9F9E8'))
    SCREEN.blit(label, ((210 - label.get_rect().width) // 2 + 114, 160))

    # Goal image
    goal = 'icons\\chip_{}.png'.format(random.choice(chip_names)) if gamemode == 1 \
        else 'textures\\cell_closed.png'
    goal_image = pygame.transform.scale(load_image(goal), (77, 77))
    SCREEN.blit(goal_image, ((210 - goal_image.get_rect().width) // 2 + 114, 210))

    # Goal counter
    count_text = '0/50' if gamemode == 1 else '0/{}'.format(str(cell_count))
    counter = font.render(count_text, 1, pygame.Color('#F9F9E8'))
    SCREEN.blit(counter, ((210 - counter.get_rect().width) // 2 + 114, 290))

    # Timer
    timer = font.render('03:00', 1, pygame.Color('#F9F9E8'))
    SCREEN.blit(timer, ((210 - timer.get_rect().width) // 2 + 114, 380))

    # Initializing level theme depending on level number
    song.stop()
    song = pygame.mixer.Sound(
        'sounds\\songs\\level_song{}.mp3'.format(str(int(save[0][7:]) % 3 + 1)))
    song.play(-1)
    # TODO: Add function for start label appearance!


def cells_init(level, cell_image):
    global cell_count

    # Function to initialize the field of cells
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

    # Function to initialize the chips on field
    chip_name_list = [] # contains chip names to check repeating
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


def menu_func(name):
    # Method to decide the function of clicked menu button
    if name == 'ng':
        # TODO: Add new game dialog!
        pass
    elif name == 'cont':
        level_init()
    elif name == 'help':
        # TODO: Add help window!
        pass
    elif name == 'options':
        # TODO: Add options window!
        pass


def pause_func():
    # TODO: Add pause window!
    pass


def hint_func():
    # TODO: Show the hint!
    pass


def terminate():
    # TODO: Add exit dialog!
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    game()