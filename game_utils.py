import pygame
import tkinter as tk

root = tk.Tk()

def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

def rotate_on_center(screen, img, top_left, angle):
    rotated_img = pygame.transform.rotate(img, angle)
    new_rectangle = rotated_img.get_rect(center = img.get_rect(topleft = top_left).center)
    screen.blit(rotated_img, new_rectangle.topleft)

def text_in_center(screen, font, text):
    render = font.render(text, 1, (0, 0, 0))
    screen.blit(render, (screen.get_width() / 2 - render.get_width() / 2, screen.get_height() / 2 - render.get_height() / 2))