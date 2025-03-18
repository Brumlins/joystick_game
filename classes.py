import pygame
import random
import math

from joystick import *
from screen import *
from constants import *


# Třída hráče
class Player:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.width = 65
        self.height = 65
        self.speed = 5
        self.color = color
        self.health = 100
        self.max_health = 100
        self.alive = True
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 10  # Počet snímků mezi střelami
        self.controls = controls  # Joystick index nebo "keyboard1"/"keyboard2"
        self.score = 0
        self.shield_active = False
        self.shield_timer = 0
        self.shield_duration = 5 * 60  # 5 sekund
        self.aim_direction = (0, -1)  # Výchozí směr míření (nahoru)
        self.aim_visible = False  # Zda je míření viditelné
    
    def draw(self, surface):
        # Vykreslení hráče
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # Vykreslení zdraví
        health_width = 50
        health_height = 5
        health_x = self.x - (health_width - self.width) // 2
        health_y = self.y - 10
        
        # Pozadí zdraví
        pygame.draw.rect(surface, WHITE, (health_x, health_y, health_width, health_height))
        
        # Aktuální zdraví
        current_health_width = (self.health / self.max_health) * health_width
        pygame.draw.rect(surface, GREEN, (health_x, health_y, current_health_width, health_height))


        # Vykreslení štítu, pokud je aktivní
        if self.shield_active:
            shield_radius = max(self.width, self.height) + 10
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            shield_alpha = 128 + 64 * math.sin(pygame.time.get_ticks() / 200)  # Pulzující efekt
            pygame.draw.circle(shield_surface, (0, 150, 255, int(shield_alpha)), 
                            (shield_radius, shield_radius), shield_radius)
            surface.blit(shield_surface, 
                        (self.x + self.width//2 - shield_radius, 
                        self.y + self.height//2 - shield_radius))
            
         # Vykreslení ukazatele míření, pokud je aktivní
        if self.aim_visible and self.alive:
            # Střed hráče
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            # Koncový bod ukazatele míření (50 pixelů od středu hráče)
            end_x = center_x + self.aim_direction[0] * 50
            end_y = center_y + self.aim_direction[1] * 50
            
            # Vykreslení čáry ukazatele míření
            pygame.draw.line(surface, self.color, (center_x, center_y), (end_x, end_y), 2)
            
            # Vykreslení malého kruhu na konci ukazatele
            pygame.draw.circle(surface, self.color, (int(end_x), int(end_y)), 3)
    
    def move(self, dx, dy):
        # Pohyb hráče s omezením na hranice obrazovky
        self.x = max(0, min(WIDTH - self.width, self.x + dx))
        self.y = max(0, min(HEIGHT - self.height, self.y + dy))
    
    def take_damage(self, amount):
        if self.alive:
            self.health -= amount
            if self.health <= 0:
                self.alive = False
    
    def shoot(self, bullets, direction):
        if self.shoot_cooldown <= 0 and self.alive:
            # Střed hráče
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            # Vytvoření nové střely
            bullet = Bullet(center_x, center_y, direction, self.color)
            bullets.append(bullet)
            
            # Nastavení cooldownu
            self.shoot_cooldown = self.shoot_cooldown_max
    
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        # Aktualizace štítu
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
        # Původní pozice
        old_x, old_y = self.x, self.y
        
    

    def activate_shield(self):
        self.shield_active = True
        self.shield_timer = self.shield_duration

    def take_damage(self, amount):
        if self.alive:
            if not self.shield_active:  # Pokud má štít, neutrpí žádné poškození
                self.health -= amount
                if self.health <= 0:
                    self.alive = False



# Třída střely
class Bullet:
    def __init__(self, x, y, direction, color):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = color
        self.speed = 20
        self.direction = direction  # Tuple (dx, dy) pro směr
        self.owner_color = color  # Pro identifikaci, komu střela patří
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
    
    def update(self):
        old_x, old_y = self.x, self.y
        
        # Výpočet nové pozice
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        
        # Pro velmi rychlé střely kontrolujeme kolize v několika bodech mezi starou a novou pozicí
        self.trajectory = []
        steps = max(1, int(self.speed / 5))  # Počet kroků závisí na rychlosti
        for i in range(steps + 1):
            t = i / steps
            point_x = old_x + (self.x - old_x) * t
            point_y = old_y + (self.y - old_y) * t
            self.trajectory.append((point_x, point_y))
    
    def is_off_screen(self):
        return (self.x < 0 or self.x > WIDTH or
                self.y < 0 or self.y > HEIGHT)




# Třída nepřítele
class Enemy:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.speed = random.uniform(1.0, 3.0)
        self.color = RED
        self.health = 50
        self.max_health = 50
        
        # Náhodná pozice na okraji obrazovky
        side = random.randint(0, 3)
        if side == 0:  # Horní strana
            self.x = random.randint(0, WIDTH - self.width)
            self.y = -self.height
        elif side == 1:  # Pravá strana
            self.x = WIDTH
            self.y = random.randint(0, HEIGHT - self.height)
        elif side == 2:  # Dolní strana
            self.x = random.randint(0, WIDTH - self.width)
            self.y = HEIGHT
        else:  # Levá strana
            self.x = -self.width
            self.y = random.randint(0, HEIGHT - self.height)
    
    def draw(self, surface):
        # Vykreslení nepřítele
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # Vykreslení zdraví
        health_width = 40
        health_height = 5
        health_x = self.x - (health_width - self.width) // 2
        health_y = self.y - 10
        
        # Pozadí zdraví
        pygame.draw.rect(surface, WHITE, (health_x, health_y, health_width, health_height))
        
        # Aktuální zdraví
        current_health_width = (self.health / self.max_health) * health_width
        pygame.draw.rect(surface, GREEN, (health_x, health_y, current_health_width, health_height))
    
    def move_towards_player(self, player_x, player_y):
        # Výpočet směru k hráči
        dx = player_x - (self.x + self.width // 2)
        dy = player_y - (self.y + self.height // 2)
        
        # Normalizace vektoru
        distance = max(1, math.sqrt(dx * dx + dy * dy))
        dx /= distance
        dy /= distance
        
        # Pohyb směrem k hráči
        self.x += dx * self.speed
        self.y += dy * self.speed
    
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0
    
    def collides_with(self, other_x, other_y, other_width, other_height):
        return (self.x < other_x + other_width and
                self.x + self.width > other_x and
                self.y < other_y + other_height and
                self.y + self.height > other_y)





# Třída pro svítící kolečko (powerup)
class PowerUp:
    def __init__(self):
        self.radius = 15
        self.color = (0, 100, 255)  # Modrá barva
        self.glow_color = (100, 200, 255)  # Světlejší modrá pro záření
        self.glow_radius = 20
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.active = True
        self.glow_alpha = 255
        self.glow_direction = -5  # Směr změny průhlednosti (pulzování)
    
    def draw(self, surface):
        if not self.active:
            return
            
        # Vykreslení záře
        glow_surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.glow_color, self.glow_alpha), 
                          (self.glow_radius, self.glow_radius), self.glow_radius)
        surface.blit(glow_surface, (self.x - self.glow_radius, self.y - self.glow_radius))
        
        # Vykreslení kolečka
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
    
    def update(self):
        if not self.active:
            return
            
        # Pulzující efekt
        self.glow_alpha += self.glow_direction
        if self.glow_alpha <= 100 or self.glow_alpha >= 255:
            self.glow_direction *= -1
    
    def collides_with(self, player):
        if not self.active:
            return False
            
        distance = math.sqrt((player.x + player.width//2 - self.x)**2 + 
                            (player.y + player.height//2 - self.y)**2)
        return distance < (player.width//2 + self.radius)





# Třída pro menu položky
class MenuItem:
    def __init__(self, text, x, y, width, height, color, hover_color, font_size=48):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.font_size = font_size
        self.is_selected = False
        self.is_hovered = False
    
    def draw(self, surface):
        # Vykreslení tlačítka
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Vykreslení ohraničení - silnější pro vybrané položky
        border_thickness = 3 if self.is_selected else 5
        border_color = WHITE if self.is_selected else BLACK
        pygame.draw.rect(surface, border_color, self.rect, border_thickness)
        
        # Vykreslení textu
        font = pygame.font.SysFont(None, self.font_size)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def check_click(self):
        return self.is_hovered and pygame.mouse.get_pressed()[0]
