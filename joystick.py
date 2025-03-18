import pygame

# Inicializace Pygame
pygame.init()
pygame.joystick.init()

# Kontrola pripojeni joysticku
joysticks = []
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    joysticks.append(joystick)
    print(f"Detekován joystick: {joystick.get_name()}")

if len(joysticks) == 0:
    print("Žádný joystick nebyl detekován! Hra bude používat klávesnici.")