import pygame
from constants import COUNTER, WIDTH, HEIGHT
ram = bytearray(4096)

pc = None

delay_timer = max(max(0, COUNTER), 255) #holder for 8-bit timer
sound_timer = max(max(0, COUNTER), 255)
current_instruction = None
registry = [0]*16

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

while True:
    pass