import pygame
from pygame import *
from random import randint, choice

pygame.init()

clock = time.Clock()

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 600
WINDOW_RES = (WINDOW_WIDTH, WINDOW_HEIGHT)

WIDTH = 100
HEIGHT = 100

RED = (255, 000, 000)
GREEN = (000, 255, 000)
WHITE = (255, 255, 255)

SPAWN_RATE = 500
FRAME_RATE = 120

REG_SPEED = 2
SLOW_SPEED = 0.5

LVL1_STARTING_BUCKS = 15
LVL2_STARTING_BUCKS = 25
BUCK_RATE = 120
STARTING_BUCK_BOOSTER = 1

MAX_BAD_REVIEWS = 3
WIN_TIME = FRAME_RATE * 60 * 3

cannon_coordinates = []
FIRE_RATE = 60


GAME_WINDOW = display.set_mode(WINDOW_RES)
display.set_caption('Attack of Vampire Pizzas!')

pizza_img = image.load('vampire.png')
pizza_surf = Surface.convert_alpha(pizza_img)
VAMPIRE_PIZZA = transform.scale(pizza_surf, (WIDTH, HEIGHT))

restaurant_img = image.load('restaurant.jpg')
restaurant_surf = Surface.convert_alpha(restaurant_img)
BACKGROUND = transform.scale(restaurant_surf, (1100,600))

pepperoni_img = image.load('pepperoni.png')
pepperoni_surf = Surface.convert_alpha(pepperoni_img)
PEPPERONI = transform.scale(pepperoni_surf, (WIDTH, HEIGHT))

garlic_img = image.load('garlic.png')
garlic_surf = Surface.convert_alpha(garlic_img)
GARLIC = transform.scale(garlic_surf, (WIDTH, HEIGHT))

pizzacutter_img = image.load('pizzacutter.png')
pizzacutter_surf = Surface.convert_alpha(pizzacutter_img)
PIZZACUTTER = transform.scale(pizzacutter_surf, (WIDTH, HEIGHT))

table_img = image.load('pizza-table.png')
table_surf = Surface.convert_alpha(table_img)
TABLE = transform.scale(table_surf, (WIDTH, HEIGHT))

explosion_img = image.load('explosion.png')
explosion_surf = Surface.convert_alpha(explosion_img)
EXPLOSION = transform.scale(explosion_surf, (WIDTH, HEIGHT))

cannon_img = image.load('anchovy-cannon.png')
cannon_surf = Surface.convert_alpha(cannon_img)
CANNON = transform.scale(cannon_surf, (WIDTH, HEIGHT))

anchovy_img = image.load('anchovy.png')
anchovy_surf = Surface.convert_alpha(anchovy_img)
ANCHOVY = transform.scale(anchovy_surf, (50, 50))



class VampireSprite(sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.speed = REG_SPEED
        self.lane = randint(0,4)
        all_vampires.add(self)
        self.image = VAMPIRE_PIZZA.copy()
        y = 50 + self.lane * 100
        self.rect = self.image.get_rect(center = (1100, y))
        self.health = 100
        self.despawn_wait = None

    def update(self, game_window, counters):
        game_window.blit(BACKGROUND,(self.rect.x, self.rect.y), self.rect)
        self.rect.x -= self.speed
        collided = sprite.spritecollide(self, all_anchovies, True)
        if collided is not None:
            for anchovy in collided:
                self.health -= 10
        if self.rect.x <= 100:
            counters.bad_reviews += 1
            self.despawn_wait = 0
        if self.despawn_wait is None:
            if self.health <= 0:
                self.image = EXPLOSION.copy()
                self.speed = 0
                self.despawn_wait = 20
            game_window.blit(self.image, (self.rect.x, self.rect.y))
        elif self.despawn_wait <= 0:
            self.kill()
        else:
            self.despawn_wait -= 1
        game_window.blit(self.image, (self.rect.x, self.rect.y))

    def attack(self, tile):
        if tile.trap == SLOW:
            self.speed = SLOW_SPEED
        if tile.trap == DAMAGE:
            self.health -= 1
        if tile.trap == MINE:
            self.health = 0
        


class Counters(object):
    def __init__(self, pizza_bucks, buck_rate, buck_booster, timer, fire_rate):
        self.fire_rate = fire_rate
        self.loop_count = 0
        self.display_font = font.Font('pizza_font.ttf', 25)
        self.pizza_bucks = pizza_bucks
        self.buck_rate = buck_rate
        self.buck_booster = buck_booster
        self.bucks_rect = None
        self.timer = timer
        self.timer_rect = None
        self.bad_reviews = 0
        self.bad_rev_rect = None

    def increment_bucks(self):
        if self.loop_count % self.buck_rate == 0:
            self.pizza_bucks += self.buck_booster

    def update_cannon(self):
        for location in cannon_coordinates:
            if self.loop_count % self.fire_rate == 0:
                Anchovy(location)

    def draw_bucks(self, game_window):
        if bool(self.bucks_rect):
            game_window.blit(BACKGROUND, (self.bucks_rect.x, self.bucks_rect.y), self.bucks_rect)
        bucks_surf = self.display_font.render(str(self.pizza_bucks), True, WHITE)
        self.bucks_rect = bucks_surf.get_rect()
        self.bucks_rect.x = WINDOW_WIDTH - 50
        self.bucks_rect.y = WINDOW_HEIGHT - 50
        game_window.blit(bucks_surf, self.bucks_rect)

    def draw_bad_reviews(self, game_window):
        if bool(self.bad_rev_rect):
            game_window.blit(BACKGROUND, (self.bad_rev_rect.x, self.bad_rev_rect.y), self.bad_rev_rect)
        bad_rev_surf = self.display_font.render(str(self.bad_reviews), True, WHITE)
        self.bad_rev_rect = bad_rev_surf.get_rect()
        self.bad_rev_rect.x = WINDOW_WIDTH - 150
        self.bad_rev_rect.y = WINDOW_HEIGHT - 50
        game_window.blit(bad_rev_surf, self.bad_rev_rect)

    def draw_timer(self, game_window):
        if bool(self.timer_rect):
            game_window.blit(BACKGROUND, (self.timer_rect.x, self.timer_rect.y), self.timer_rect)
        timer_surf = self.display_font.render(str((WIN_TIME - self.loop_count) // FRAME_RATE), True, WHITE)
        self.timer_rect = timer_surf.get_rect()
        self.timer_rect.x = WINDOW_WIDTH - 250
        self.timer_rect.y = WINDOW_HEIGHT - 50
        game_window.blit(timer_surf, self.timer_rect)

    def update(self, game_window):
        self.loop_count += 1
        self.increment_bucks()
        self.draw_bucks(game_window)
        self.draw_bad_reviews(game_window)
        self.draw_timer(game_window)
        self.update_cannon()
        


class Trap(object):
    def __init__(self, trap_kind, cost, trap_img):
        self.trap_kind = trap_kind
        self.cost = cost
        self.trap_img = trap_img



class TrapApplicator(object):
    def __init__(self):
        self.selected = None
                                                            
    def select_trap(self, trap):
        if trap.cost <= counter.pizza_bucks:
            self.selected = trap

    def select_tile(self, tile, counters):
        self.selected = tile.set_trap(self.selected, counters)
        
        
        
class BackgroundTile(sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.trap = None
        self.rect = rect



class PlayTile(BackgroundTile):

    def set_trap(self, trap, counters):
        if bool(trap) and not bool(self.trap):
            counters.pizza_bucks -= trap.cost
            self.trap = trap
            if trap == EARN:
                counters.buck_booster += 1
            if trap == PROJECTILE:
                cannon_coordinates.append((self.rect.x, self.rect.y))
        return None

    def draw_trap(self, game_window, trap_applicator):
        if bool(self.trap):
            game_window.blit(self.trap.trap_img, (self.rect.x, self.rect.y))



class ButtonTile(BackgroundTile):

    def set_trap(self, trap, counters):
        if counters.pizza_bucks >= self.trap.cost:
            return self.trap
        else:
            return None
        
    def draw_trap(self, game_window, trap_applicator):
        if bool(trap_applicator.selected):
            if trap_applicator.selected == self.trap:
                draw.rect(game_window, (238, 190, 47), (self.rect.x, self.rect.y, WIDTH, HEIGHT), 5)


                
class InactiveTile(BackgroundTile):

        def set_trap(self, trap, counters):
            return None

        def draw_trap(self, game_window, trap_applicator):
            pass



class Anchovy(sprite.Sprite):
    def __init__(self, coordinates):
        super().__init__()
        self.image = ANCHOVY.copy()
        self.speed = REG_SPEED
        all_anchovies.add(self)
        self.rect = self.image.get_rect()
        self.rect.x = coordinates[0] + 40
        self.rect.y = coordinates[1] + 40

    def update(self, game_window):
        game_window.blit(BACKGROUND, (self.rect.x, self.rect.y), self.rect)
        self.rect.x += self.speed
        if self.rect.x > 1200:
            self.kill()
        else:
            game_window.blit(self.image, (self.rect.x, self.rect.y))
                
    

all_vampires = sprite.Group()
all_anchovies = sprite.Group()


lvl1_enemy_types = []
lvl1_enemy_types.append(VampireSprite)
lvl2_enemy_types = []
lvl2_enemy_types.append(VampireSprite)


SLOW = Trap('SLOW', 5, GARLIC)
DAMAGE = Trap('DAMAGE', 3, PIZZACUTTER)
EARN = Trap('EARN', 7, PEPPERONI)
MINE = Trap('MINE', 10, TABLE)
PROJECTILE = Trap('PROJECTILE', 8, CANNON)

trap_applicator = TrapApplicator()
tile_grid = []
tile_color = WHITE

for row in range(6):
    row_of_tiles = []                                               
    tile_grid.append(row_of_tiles)
    for column in range(11):
        tile_rect = Rect(WIDTH * column, HEIGHT * row, WIDTH, HEIGHT)
        if column <= 1:
            new_tile = InactiveTile(tile_rect)
        else:
            if row == 5:
                if 2 <= column <= 6:
                    new_tile = ButtonTile(tile_rect)
                    new_tile.trap = [SLOW, DAMAGE, EARN, MINE, PROJECTILE][column - 2]
                else:
                    new_tile = InactiveTile(tile_rect)
            else:
                new_tile = PlayTile(tile_rect)
        row_of_tiles.append(new_tile) 
        if row == 5 and 2 <= column <= 6:
            BACKGROUND.blit(new_tile.trap.trap_img, (new_tile.rect.x, new_tile.rect.y))
            if column != 0 and row != 5:
                if column != 1:
                    draw.rect(BACKGROUND, tile_color, (WIDTH * column, HEIGHT * row, WIDTH, HEIGHT), 1)







def run_level(enemy_list, start_bucks, clear_tiles):
    GAME_WINDOW.blit(BACKGROUND, (0,0))
    counters = Counters(start_bucks, BUCK_RATE, STARTING_BUCK_BOOSTER, WIN_TIME)
    for vampire in all vampires:
        vampire.kill()
    if clear_tiles:
        for row in tile_grid:
            for column_index in range(len(row)):
                if isinstance(row[column_index], PlayTile):
                    row[column_index].trap = None

    game_running = True
    program_running = True
    while game_running:
        for event in pygame.event.get():
            if event.type == QUIT:   
                game_running = False
                program_running = False
            elif event.type == MOUSEBUTTONDOWN:
                coordinates = mouse.get_pos()
                x = coordinates[0]
                y = coordinates[1]
                tile_y = y // 100
                tile_x = x // 100
                trap_applicator.select_tile(tile_grid[tile_y][tile_x], counters)
            elif event.type == KEYDOWN:
                if event.key == K_1:
                    trap_applicator.select_tile(tile_grid[5][2], counters)
                if event.key == K_2:
                    trap_applicator.select_tile(tile_grid[5][3], counters)
                if event.key == K_3:
                    trap_applicator.select_tile(tile_grid[5][4], counters)
                if event.key == K_4:
                    trap_applicator.select_tile(tile_grid[5][5], counters)

        if randint(1, SPAWN_RATE) == 1:
            choice(enemy_list)()
        
        for tile_row in tile_grid:
            for tile in tile_row:
                if bool(tile.trap):
                    GAME_WINDOW.blit(BACKGROUND, (tile.rect.x, tile.rect.y), tile.rect)

                

        for vampire in all_vampires:
            tile_row = tile_grid[vampire.rect.y // 100]
            vamp_left_side = vampire.rect.x // 100
            vamp_right_side = (vampire.rect.x + vampire.rect.width) // 100
            if 0 <= vamp_left_side <=10:
                left_tile = tile_row[vamp_left_side]
            else:
                left_tile = None
            if 0 <= vamp_right_side <= 10:
                right_tile = tile_row[vamp_right_side]
            else:
                right_tile = None

            if bool(left_tile):
                vampire.attack(left_tile)
            if bool(right_tile):
                if right_tile != left_tile:
                    vampire.attack(right_tile)

        if counters.bad_reviews >= MAX_BAD_REVIEWS:
            game_running = False
        if counters.loop_count > WIN_TIME:
            game_running = False



        for vampire in all_vampires:
            vampire.update(GAME_WINDOW, counters)

        for tile_row in tile_grid:
            for tile in tile_row:
                tile.draw_trap(GAME_WINDOW, trap_applicator)

        for anchovy in all_anchovies:
            anchovy.update(GAME_WINDOW)


     
        counters.update(GAME_WINDOW) #FIX THIS LATER

        display.update()

        clock.tick(FRAME_RATE)

    return game_running, program_running, counters

leverl_setup = [[lvl1_enemy_types, LVL1_STARTING_BUCKS], [lvl2_enemy_types, LVL2_STARTING_BUCKS]

current_level = 0



end_font = font.Font('pizza_font.ttf', 50)
program_running = True
while program and current_level < len(Level_setup):
    if current_level > 0:
        clear_tiles = True
    else:
        clear_tiles = False
    game_running, program_running, counters = run_level(level_setup[current_level][0], level_setup[current_level][1], clear_tiles)
    if program_running:
        if counters.bad_reviews >= MAX_BAD_REVIEWS:
            end_surf = end_font.render('Game Over', True, WHITE)
            game_running = False
            GAME_WINDOW.blit(end_surf, (350, 200))
            display.update()
        elif current_level < len(level_setup):
            cont_surf = end_font.render('Press Ender for Level' + str(current_level + 1), True, WHITE)
            GAME_WINDOW.blit(cont_surf, (150, 400))
            display.update
            #left off here



while program_running:
    for event in pygame.event.get():
        if event.type == QUIT:
            program_running = False
    clock.tick(FRAME_RATE)





pygame.quit()

