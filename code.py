import pygame
import math
import time
from game_utils import scale_image, rotate_on_center, text_in_center

pygame.init()
pygame.font.init()
font_size = 30
main_font = pygame.font.SysFont("comicsans", int(font_size))
pygame.display.set_caption('Dont Stop Me Now! (1.0.0)' )
car = pygame.image.load('assets/red-car.png')
car = scale_image(car, 0.55)
comp_car = pygame.image.load('assets/grey-car.png')
comp_car = scale_image(comp_car, 0.55)
finish_line = pygame.image.load('assets/finish.png')
finish_line = scale_image(finish_line, 0.75)
finish_line_mask = pygame.mask.from_surface(finish_line)
grass = pygame.image.load('assets/grass.jpg')
grass = scale_image(grass, 1.7)
track = pygame.image.load('assets/track.png')
track = scale_image(track, 0.75)
trackborder = pygame.image.load('assets/track-border.png')
trackborder = scale_image(trackborder, 0.75)
trackborder_mask = pygame.mask.from_surface(trackborder)
screen = pygame.display.set_mode((695, 690))
clock = pygame.time.Clock()

images_to_render = [(grass, (0, 0)), (track, (20, 10)), (finish_line, (130, 240)), (trackborder, (20, 10))]
x = 0
path = [(158, 114), (120, 58), (77, 112), (71, 404), (276, 616), (343, 616), (349, 455), (435, 405), (519, 443), (531, 593), (581, 604), (613, 575), (633, 347), (580, 313), (388, 303), (344, 245), (449, 224), (609, 229), (618, 87), (282, 71), (247, 113), (253, 315), (212, 333), (173, 318),  (165, 248)]

running = True

class GameInfo:
    def __init__(self, level = 1):
        self.level = level
        self.current_level = level
        self.started = False
        self.level_start_time = 0
        self.LEVELS = 5

    def next_level(self):
        self.level += 1
        self.current_level = self.level
        self.started = False
        player_car.increase_speed(self.level)
        ai_car.increase_speed(self.level)
        pygame.time.wait(2000)

    def keep_level(self):
        self.current_level = self.level
        self.started = False
        pygame.time.wait(2000)

    def reset(self):
        self.level = self.current_level
        self.started = False

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        print(ai_car.max_vel)
        self.started = True
        self.level_start_time = 0
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)

class AbstractCar:
    def __init__(self, max_vel, rot_vel):
        self.max_vel = max_vel
        self.rot_vel = rot_vel
        self.vel = 0
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.base_max_vel = max_vel
        self.base_rot_vel = rot_vel

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

    def collide(self, mask, mask_top_left_x=0, mask_top_left_y=0):
        rotated_image = pygame.transform.rotate(self.IMG, self.angle)
        car_mask = pygame.mask.from_surface(rotated_image)
        rotated_rect = rotated_image.get_rect(
            center=(self.x + self.IMG.get_width() / 2, self.y + self.IMG.get_height() / 2))

        offset = (int(rotated_rect.left - mask_top_left_x), int(rotated_rect.top - mask_top_left_y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0

class PlayerCar(AbstractCar):
    IMG = car
    START_POS = (171, 180)

    def bounce(self):
        self.vel = self.vel / 2
        self.move()

    def increase_speed(self, level):
        level_factor = level - 1
        self.max_vel = self.base_max_vel + (level_factor * 0.2)  # Smaller increase for player
        self.rot_vel = self.base_rot_vel + (level_factor * 0.3)

class ComputerCar(AbstractCar):
    IMG = comp_car
    START_POS = (141, 180)
    finished = False

    def __init__(self, max_vel, rot_vel, path = []):
        super().__init__(max_vel, rot_vel)
        self.path = path
        self.current_point =  0
        self.vel = max_vel
        self.on_level = 1

    def increase_speed(self, level):
        level_factor = level - 1
        self.max_vel = self.base_max_vel + (level_factor * 0.23)  # Medium increase for AI
        self.rot_vel = self.base_rot_vel + (level_factor * 0.4)

    def bounce(self):
        self.vel = self.vel / 2
        self.move()

    #def draw_points(self, screen):
    #    for point in self.path:
    #        pygame.draw.circle(screen, (255, 0, 0), point, 5)

    def draw(self, screen):
        super().draw(screen)
        #self.draw_points(screen)

    def move(self):
        if self.on_level > game_info.current_level:
            self.vel = 0
        else:
            self.vel = self.max_vel
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

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rot_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rot_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.IMG.get_width(), self.IMG.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def reset(self):
        super().reset()
        self.current_point = 0
        self.finished = False

def draw(screen, images, player_car, ai_car):
    screen.fill((0, 0, 0))

    for img,pos in images:
        screen.blit(img, pos)

    levels_text = main_font.render(f"There are {game_info.LEVELS} Levels", 1, (0, 0, 0))
    screen.blit(levels_text, (10, screen.get_height() - levels_text.get_height() - 5))

    level_text = main_font.render(f"Level {game_info.level}", 1, (0, 0, 0))
    screen.blit(level_text, (10, screen.get_height() - level_text.get_height() - 75))

    time_text = main_font.render(f"Time =  {game_info.get_level_time()}", 1, (0, 0, 0))
    screen.blit(time_text, (10, screen.get_height() - time_text.get_height() - 40))

    player_car.draw(screen)
    ai_car.draw(screen)
    pygame.display.update()

def finish_collisions(player_car, ai_car, game_info):
    ai_finish_poi_collide = ai_car.collide(finish_line_mask, 130, 240)
    if ai_finish_poi_collide != None:
        ai_car.finished = True
    player_finish_poi_collide = player_car.collide(finish_line_mask, 130, 240)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            draw(screen, images_to_render, player_car, ai_car)
            player_car.bounce()
        else:
            if ai_car.finished:
                player_car.reset()
                ai_car.reset()
                game_info.keep_level()
            else:
                player_car.reset()
                ai_car.reset()
                game_info.next_level()
                ai_car.on_level += 1

player_car = PlayerCar(1.8, 3)
game_info = GameInfo()
ai_car = ComputerCar(1.7, 3, path)

while running:
    clock.tick(60)

    draw(screen, images_to_render, player_car, ai_car)

    while not game_info.started:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                game_info.start_level()
                break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #if event.type == pygame.MOUSEBUTTONDOWN:
        #    pos = pygame.mouse.get_pos()
        #   ai_car.path.append(pos)

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

    if player_car.collide(trackborder_mask,  20, 10) != None:
        player_car.bounce()

    finish_collisions(player_car, ai_car, game_info)

    if game_info.game_finished():
        text_in_center(screen, main_font, f"You Completed The Game!")
        pygame.time.wait(10000)
        running = False
        break

    pygame.display.update()

#print(ai_car.path)
pygame.quit()

