import pygame
import math
from game_utils import scale_image, for_screen, rotate_on_center

pygame.init()
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

running = True

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
        self.vel = min(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.x -= horizontal
        self.y -= vertical

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 1.2, 0)
        self.move()

    def collide(self, mask, x = 0, y = 0):
        car_mask = pygame.mask.from_surface(self.IMG)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def bounce(self):
        self.vel = -self.vel / 2
        self.move()

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0

class PlayerCar(AbstractCar):
    IMG = car
    START_POS = (for_screen(690, 160, "h"), for_screen(690, 200, "h"))

class ComputerCar(AbstractCar):
    IMG = car
    START_POS = (for_screen(690, 130, "h"), for_screen(690, 200, "h"))

    def __init__(self, max_vel, rot_vel, path = []):
        super().__init__(max_vel, rot_vel)
        self.path = path
        self.current_point =  0
        self.vel = 0

    def draw_points(self, screen):
        for point in self.path:
            pygame.draw.circle(screen, (255, 0, 0), point, 5)

    def draw(self, screen):
        super().draw(screen)
        self.draw_points(screen)


def draw(screen, images, player_car, ai_car):
    for img,pos in images:
        screen.blit(img, pos)

    player_car.draw(screen)
    ai_car.draw(screen)
    pygame.display.update()

player_car = PlayerCar(8, 6)
ai_car = ComputerCar(8, 6)

while running:
    screen.fill((0,0,0))

    draw(screen, images_to_render, player_car, ai_car)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            ai_car.path.append(pos)

    keys = pygame.key.get_pressed()
    moved = False

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

    finish_poi_collide = player_car.collide(finish_line_mask, 180, 360)
    if finish_poi_collide != None:
        if finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            player_car.reset()


    clock.tick(60)

print(ai_car.path)
pygame.quit()

