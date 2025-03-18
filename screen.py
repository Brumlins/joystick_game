import pygame

# zjisteni rozliseni a nastaveni fullscreenu
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
WIDTH, HEIGHT = monitor_size[0], monitor_size[1]
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Xbox Joystick Hra")