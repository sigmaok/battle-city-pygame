import pygame
from random import randint
from game.types import Types
from game.constants import *

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
HIT_BOX_SIDE = 32

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

font = pygame.font.Font(None, 30)
img_brick = pygame.image.load('img/block_brick.png')

img_tanks1 = [pygame.image.load(f'img/tank{i}.png') for i in range(1, 9)]
img_tanks2 = [pygame.image.load(f'img/tank_{i}.png') for i in range(1, 9)]

img_tanks1 = [pygame.transform.scale(img, (29, 32)) for img in img_tanks1]
img_tanks2 = [pygame.transform.scale(img, (29, 32)) for img in img_tanks2]

img_bangs = [pygame.image.load(f'img/bang{i}.png') for i in range(1, 4)]

img_bonuses = [
    pygame.image.load(f'img/bonus_star.png'),
    pygame.image.load(f'img/bonus_tank.png')
]

img_bullet = pygame.image.load('img/bullet.png')
gm = pygame.image.load('img/game-over.png')
gm_rect = gm.get_rect()

gm_x = (WIDTH - gm.get_width()) // 2
gm_y = (HEIGHT - gm.get_height()) // 2

class UI:
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        i = 0
        for obj in objects:
            if obj.type == Types.TANK:
                pygame.draw.rect(screen, obj.color, (5 + i * 70, 5, 22, 22))

                text = font.render(str(obj.rank), 1, 'black')
                rect = text.get_rect(center=(5 + i * 70 + 11, 5 + 11))
                screen.blit(text, rect)

                text = font.render(str(obj.hp), 1, obj.color)
                rect = text.get_rect(center=(5 + i * 70 + 32, 5 + 11))
                screen.blit(text, rect)

                i += 1


class Tank:
    def __init__(self, x, y, color, direction: int, key_list, img_tanks):
        objects.append(self)
        self.type = Types.TANK
        self.rect = pygame.Rect(x, y, HIT_BOX_SIDE, HIT_BOX_SIDE)
        self.color = color
        self.speed = 2
        self.direction = direction
        self.img_tanks = img_tanks

        self.key_left = key_list[0]
        self.key_right = key_list[1]
        self.key_up = key_list[2]
        self.key_down = key_list[3]
        self.key_shoot = key_list[4]

        self.bullet_speed = 5
        self.bullet_damage = 1

        self.shoot_timer = 0
        self.shoot_cooldown = 60

        self.hp = 5

        self.rank = 1
        self.image = pygame.transform.rotate(self.img_tanks[self.rank], -self.direction * 90)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.image = pygame.transform.rotate(self.img_tanks[self.rank], -self.direction * 90)
        self.image = pygame.transform.scale(self.image, (HIT_BOX_SIDE-2, HIT_BOX_SIDE))
        self.rect = self.image.get_rect(center=self.rect.center)

        self.speed = MOVE_SPEED[self.rank]
        self.shoot_cooldown = SHOOT_COOLDOWN[self.rank]
        self.bullet_speed = BULLET_SPEED[self.rank]
        self.bullet_damage = BULLET_DAMAGE[self.rank]

        old_x, old_y = self.rect.topleft

        if keys[self.key_left]:
            self.rect.x -= self.speed
            self.direction = 3
        elif keys[self.key_right]:
            self.rect.x += self.speed
            self.direction = 1
        elif keys[self.key_up]:
            self.rect.y -= self.speed
            self.direction = 0
        elif keys[self.key_down]:
            self.rect.y += self.speed
            self.direction = 2

        if keys[self.key_shoot] and self.shoot_timer == 0:
            dx = DIRECTIONS[self.direction][0] * self.bullet_speed
            dy = DIRECTIONS[self.direction][1] * self.bullet_speed
            Bullet(self, self.rect.centerx, self.rect.centery - 5, dx, dy, self.bullet_damage, self.direction)
            self.shoot_timer = self.shoot_cooldown

        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        for obj in objects:
            if obj != self and obj.type == Types.BLOCK and self.rect.colliderect(obj.rect):
                self.rect.topleft = old_x, old_y
            elif self.rect.x < 0 or self.rect.x > WIDTH:
                self.rect.topleft = old_x, old_y
            elif self.rect.y < 0 or self.rect.y > HEIGHT:
                self.rect.topleft = old_x, old_y

    def draw(self):
        screen.blit(self.image, self.rect)

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            objects.remove(self)
            global win
            win = True
            screen.blit(gm, (100, 100))


class Bullet:
    def __init__(self, tank_reference, x, y, vector_x, vector_y, damage, direction):
        bullets.append(self)
        self.x, self.y = x, y
        self.rect = pygame.Rect(x, y, HIT_BOX_SIDE, HIT_BOX_SIDE)
        self.vector_x, self.vector_y = vector_x, vector_y
        self.damage = damage
        self.tank_reference = tank_reference
        self.direction = direction

        self.image = pygame.transform.rotate(img_bullet, -self.direction * 90)

    def update(self):
        self.image = pygame.transform.rotate(img_bullet, -self.direction * 90)

        self.x += self.vector_x
        self.y += self.vector_y

        if self.x < 0 or self.y < 0 or self.x > WIDTH or self.y > HEIGHT:
            bullets.remove(self)
        else:
            for obj in objects:
                if (obj != self.tank_reference and obj.type != Types.BANG
                        and obj.type != Types.BONUS and obj.rect.collidepoint(self.x, self.y)):
                    obj.take_damage(self.damage)
                    bullets.remove(self)
                    Bang(self.x, self.y)
                    break

    def draw(self):
        screen.blit(self.image, (self.x, self.y))
        # pygame.draw.circle(screen, 'yellow', (self.x, self.y), 2)


class Bang:
    def __init__(self, x, y):
        objects.append(self)
        self.type = Types.BANG

        self.x, self.y = x, y
        self.current_frame = 0

    def update(self):
        self.current_frame += 0.1
        if self.current_frame >= 3:
            objects.remove(self)

    def draw(self):
        image = img_bangs[int(self.current_frame)]
        rect = image.get_rect(center=(self.x, self.y))
        screen.blit(image, rect)


class Block:
    def __init__(self, x, y, size):
        self.type = Types.BLOCK

        self.rect = pygame.Rect(x, y, size, size)
        self.hp = 1

    def update(self):
        pass

    def draw(self):
        screen.blit(img_brick, self.rect)
        # pygame.draw.rect(screen, 'green', self.rect)
        # pygame.draw.rect(screen, 'gray20', self.rect, 2)

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0: objects.remove(self)


class Bonus:
    def __init__(self, px, py, bonus_idx):
        objects.append(self)
        self.type = Types.BONUS

        self.image = img_bonuses[bonus_idx]
        self.rect = self.image.get_rect(center=(px, py))

        self.timer = 600
        self.bonus_idx = bonus_idx

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            objects.remove(self)

        for obj in objects:
            if obj.type == Types.TANK and self.rect.colliderect(obj.rect):
                if self.bonus_idx == 0:
                    if obj.rank < len(img_tanks1) - 1:
                        obj.rank += 1
                        objects.remove(self)
                        break
                elif self.bonus_idx == 1:
                    obj.hp += 1
                    objects.remove(self)
                    break

    def draw(self):
        if self.timer % 30 < 15:
            screen.blit(self.image, self.rect)


bullets = []
objects = []

Tank(100, 275, 'orange', 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), img_tanks1)
Tank(650, 275, 'blue', 0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_KP_ENTER), img_tanks2)

from game.map import map_setting

ui = UI()

for block in map_setting:
    objects.append(block)

play = True
win = False

bonus_timer = 180
while play:
    print(win)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False

    keys = pygame.key.get_pressed()
    if bonus_timer > 0:
        bonus_timer -= 1
    else:
        Bonus(randint(50, WIDTH - 50), randint(50, HEIGHT - 50), randint(0, len(img_bonuses) - 1))
        bonus_timer = randint(120, 240)

    for bullet in bullets:
        bullet.update()

    for obj in objects:
        obj.update()
    ui.update()

    screen.fill("black")
    for bullet in bullets:
        bullet.draw()

    for obj in objects:
        obj.draw()
    ui.draw()

    if not win:
        pygame.display.update()
    else:
        screen.fill((0, 0, 0))
        screen.blit(gm, (gm_x, gm_y))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
