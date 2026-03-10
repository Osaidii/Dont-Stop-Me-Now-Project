import pygame
import math
import time
from game_utils import scale_image, for_screen, rotate_on_center, text_in_center

pygame.init()
pygame.font.init()
main_font = pygame.font.SysFont("comicsans", 44)
pygame.display.set_caption('Dont Stop Me Now! (1.0.0)' )
car = pygame.image.load('car_for_now.png')
car = scale_image(car, for_screen(690, 2, "h"))
finish_line = pygame.image.load('finish.png')
finish_line = scale_image(finish_line, for_screen(690, 0.75, "h"))
finish_line_mask = pygame.mask.from_surface(finish_line)
grass = pygame.image.load('grass.jpg')
grass = scale_image(grass, for_screen(690, 1.7, "h"))
track = pygame.image.load('track.png')
track = scale_image(track, for_screen(690, 0.75, "h"))
trackborder = pygame.image.load('track-border.png')
trackborder = scale_image(trackborder, for_screen(690, 0.75, "h"))
trackborder_mask = pygame.mask.from_surface(trackborder)
screen = pygame.display.set_mode((for_screen(690, 695, "h"), for_screen(690, 690, "h")))
clock = pygame.time.Clock()

delta_time = 0.1
images_to_render = [(grass, (0, 0)), (track, (20, 10)), (finish_line, (180, 360)), (trackborder, (20, 10))]
x = 0
path = [(239, 159), (176, 101), (88, 173), (93, 605), (380, 882), (470, 902), (527, 801), (539, 658), (634, 605), (758, 659), (775, 868), (835, 932), (933, 912), (930, 499), (861, 448), (563, 459), (507, 390), (572, 333), (882, 348), (938, 272), (920, 122), (428, 109), (375, 163), (385, 462), (300, 533), (224, 467), (234, 375)]
running = True

class GameInfo:
    def __init__(self, level = 0):
        self.level = level
        self.current_level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.current_level = self.level
        self.started = False

    def reset(self):
        self.level = self.current_level
        self.started = False

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.started = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return self.level_start_time - time.time()


class AbstractCar:
    def __init__(self, max_vel, rot_vel):
        self.max_vel = max_vel
        self.rot_vel = rot_vel
        self.vel = 0
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left = False, right = False):
        if left:
            self.angle += self.rot_vel
        if right:
            self.angle -= self.rot_vel

    def draw(self, screen):
        rotate_on_center(screen, self.IMG, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.x -= horizontal
        self.y -= vertical

    def reduce_speed(self):
        if self.vel > 0:
            self.vel = max(self.vel - self.acceleration / 1.2, 0)
        elif self.vel < 0:
            self.vel = min(self.vel + self.acceleration / 0.5, 0)
        self.move()

    def collide(self, mask, x = 0, y = 0):
        car_mask = pygame.mask.from_surface(self.IMG)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0

class PlayerCar(AbstractCar):
    IMG = car
    START_POS = (for_screen(690, 160, "h"), for_screen(690, 200, "h"))

    def bounce(self):
        self.vel = self.vel / 2
        self.move()

class ComputerCar(AbstractCar):
    IMG = car
    START_POS = (for_screen(690, 130, "h"), for_screen(690, 200, "h"))

    def __init__(self, max_vel, rot_vel, path = []):
        super().__init__(max_vel, rot_vel)
        self.path = path
        self.current_point =  0
        self.vel = max_vel

    def bounce(self):
        self.vel = self.vel / 2
        self.move()

    def draw_points(self, screen):
        for point in self.path:
            pygame.draw.circle(screen, (255, 0, 0), point, 5)

    def draw(self, screen):
        super().draw(screen)
        self.draw_points(screen)

    def move(self):
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_path_point()
        super().move()

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y >= self.y:
            desired_radian_angle += math.pi

        differnce_in_angle = self.angle - math.degrees(desired_radian_angle)
        if differnce_in_angle >= 180:
            differnce_in_angle -= 360

        if differnce_in_angle > 0:
            self.angle -= min(self.rot_vel, abs(differnce_in_angle))
        else:
            self.angle += min(self.rot_vel, abs(differnce_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.IMG.get_width(), self.IMG.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

def draw(screen, images, player_car, ai_car):
    for img,pos in images:
        screen.blit(img, pos)

    player_car.draw(screen)
    ai_car.draw(screen)
    pygame.display.update()

def finish_collisions(player_car, ai_car):
    computer_finish_poi_collide = ai_car.collide(finish_line_mask, 180, 360)
    if computer_finish_poi_collide != None:
        ai_car.reset()
        ai_car.current_point = 0

    player_finish_poi_collide = player_car.collide(finish_line_mask, 180, 360)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            player_car.reset()
            ai_car.reset()

player_car = PlayerCar(5.5, 5)
ai_car = ComputerCar(5, 5, path)
game_info = GameInfo()

while running:
    screen.fill((0,0,0))

    draw(screen, images_to_render, player_car, ai_car)

    while not game_info.started:
        text_in_center(screen, main_font, f"To Next Level!")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            ai_car.path.append(pos)

    keys = pygame.key.get_pressed()
    moved = False

    ai_car.move()

    if keys[pygame.K_a]:
        player_car.rotate(left = True)
    if keys[pygame.K_s]:
        player_car.move_backward()
        moved = True
    if keys[pygame.K_d]:
        player_car.rotate(right = True)
    if keys[pygame.K_w]:
        player_car.move_forward()
        moved = True

    if not moved:
        player_car.reduce_speed()

    if player_car.collide(trackborder_mask, 20, 10) != None:
        player_car.bounce()

    finish_collisions(player_car, ai_car)

    clock.tick(60)

print(ai_car.path)
pygame.quit()

