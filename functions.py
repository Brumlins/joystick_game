from classes import *
import sys


# Funkce pro vykreslení textu
def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)


# Hlavní herní smyčka
def main():
    global game_state
    
    clock = pygame.time.Clock()
    FPS = 60
    
    # Proměnné pro hru
    players = []
    bullets = []
    enemies = []
    enemy_spawn_timer = 0
    enemy_spawn_delay = 120

    powerups = []
    powerup_spawn_timer = 0
    powerup_spawn_delay = 10 * FPS  # Každých 10 sekund
    
    # Menu položky
    menu_items = [
        MenuItem("Kooperace", WIDTH // 2 - 150, HEIGHT // 2, 300, 60, PURPLE, PURPLE),
        MenuItem("Proti sobě", WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60, PURPLE, PURPLE),
        MenuItem("Ukončit", WIDTH // 2 - 150, HEIGHT // 2 + 200, 300, 60, PURPLE, (200, 100, 200))
    ]
    
    pause_items = [
        MenuItem("Pokračovat", WIDTH // 2 - 150, HEIGHT // 2, 300, 60, PURPLE, (100, 255, 100)),
        MenuItem("Menu", WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60, PURPLE, (255, 255, 100)),
        MenuItem("Ukončit", WIDTH // 2 - 150, HEIGHT // 2 + 200, 300, 60, PURPLE, (200, 100, 200))
    ]
    
    game_over_items = [
        MenuItem("Hrát znovu", WIDTH // 2 - 150, HEIGHT // 2, 300, 60, PURPLE, (100, 255, 100)),
        MenuItem("Menu", WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60, PURPLE, (255, 255, 100))
    ]
    
    # Proměnné pro ovládání menu joystickem
    selected_item = 0
    joystick_cooldown = 0
    joystick_cooldown_max = 15  # Počet snímků mezi pohyby v menu
    
    # Hlavní herní smyčka
    running = True
    while running:
        # Zpracování událostí
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Kontrola tlačítek joysticku pro pauzu
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 7:  # Start tlačítko na Xbox ovladači
                    if game_state in [GAME_COOP, GAME_VS]:
                        game_state = PAUSED
                        selected_item = 0  # Reset vybrané položky v menu
                    elif game_state == PAUSED:
                        game_state = GAME_COOP if len(enemies) > 0 else GAME_VS
                
                # Tlačítko A pro výběr položky v menu
                if event.button == 0:  # A tlačítko
                    if game_state == MENU:
                        if selected_item == 0:  # Kooperace
                            game_state = GAME_COOP
                            # Inicializace kooperativního módu
                            players = [
                                Player(WIDTH // 4, HEIGHT // 2, BLUE, 0 if joysticks else "keyboard1"),
                                Player(3 * WIDTH // 4, HEIGHT // 2, GREEN, 1 if len(joysticks) > 1 else "keyboard2")
                            ]
                            bullets = []
                            enemies = []
                            enemy_spawn_timer = 0
                        elif selected_item == 1:  # Proti sobě
                            game_state = GAME_VS
                            # Inicializace módu proti sobě
                            players = [
                                Player(WIDTH // 4, HEIGHT // 2, BLUE, 0 if joysticks else "keyboard1"),
                                Player(3 * WIDTH // 4, HEIGHT // 2, RED, 1 if len(joysticks) > 1 else "keyboard2")
                            ]
                            bullets = []
                            enemies = []
                        elif selected_item == 2:  # Ukončit
                            running = False
                    
                    elif game_state == PAUSED:
                        if selected_item == 0:  # Pokračovat
                            game_state = GAME_COOP if len(enemies) > 0 else GAME_VS
                        elif selected_item == 1:  # Menu
                            game_state = MENU
                            selected_item = 0  # Reset vybrané položky v menu
                        elif selected_item == 2:  # Ukončit
                            running = False
            
            # Klávesnice pro pauzu (záložní možnost)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    if game_state in [GAME_COOP, GAME_VS]:
                        game_state = PAUSED
                        selected_item = 0  # Reset vybrané položky v menu
                    elif game_state == PAUSED:
                        game_state = GAME_COOP if len(enemies) > 0 else GAME_VS
        
        # Ovládání menu joystickem
        if joysticks and (game_state == MENU or game_state == PAUSED or all(not player.alive for player in players) or len([p for p in players if p.alive]) <= 1):
            joystick = joysticks[0]  # Používáme první joystick pro menu
            
            # Pohyb v menu pomocí d-padu nebo levé páčky
            y_axis = joystick.get_axis(1)  # Vertikální osa levé páčky
            
            if joystick_cooldown <= 0:
                if y_axis > 0.5 or joystick.get_hat(0)[1] == -1:  # Dolů
                    max_items = len(menu_items) - 1 if game_state == MENU else (len(pause_items) - 1 if game_state == PAUSED else len(game_over_items) - 1)
                    selected_item = min(selected_item + 1, max_items)
                    joystick_cooldown = joystick_cooldown_max
                elif y_axis < -0.5 or joystick.get_hat(0)[1] == 1:  # Nahoru
                    selected_item = max(selected_item - 1, 0)
                    joystick_cooldown = joystick_cooldown_max
            
            if joystick_cooldown > 0:
                joystick_cooldown -= 1

        
        # Aktualizace stavu hry podle herního stavu
        if game_state == MENU:
            # Vykreslení menu
            screen.fill(BLACK)
            draw_text(screen, "XBOX JOYSTICK HRA", 72, WIDTH // 2, HEIGHT // 4)
            
            # Aktualizace a vykreslení položek menu
            mouse_pos = pygame.mouse.get_pos()
            for i, item in enumerate(menu_items):
                # Nastavení výběru položky
                item.is_selected = (i == selected_item)
                
                # Kontrola myši
                if item.check_hover(mouse_pos) and pygame.mouse.get_pressed()[0]:
                    if i == 0:  # Kooperace
                        game_state = GAME_COOP
                        # Inicializace kooperativního módu
                        players = [
                            Player(WIDTH // 4, HEIGHT // 2, BLUE, 0 if joysticks else "keyboard1"),
                            Player(3 * WIDTH // 4, HEIGHT // 2, GREEN, 1 if len(joysticks) > 1 else "keyboard2")
                        ]
                        bullets = []
                        enemies = []
                        enemy_spawn_timer = 0
                    elif i == 1:  # Proti sobě
                        game_state = GAME_VS
                        # Inicializace módu proti sobě
                        players = [
                            Player(WIDTH // 4, HEIGHT // 2, BLUE, 0 if joysticks else "keyboard1"),
                            Player(3 * WIDTH // 4, HEIGHT // 2, RED, 1 if len(joysticks) > 1 else "keyboard2")
                        ]
                        bullets = []
                        enemies = []
                    elif i == 2:  # Ukončit
                        running = False
                
                # Vykreslení položky
                item.draw(screen)
            
            # Instrukce pro joystick
            draw_text(screen, "Použijte joystick pro navigaci a tlačítko A pro výběr", 36, WIDTH // 2, HEIGHT - 100)
        
        elif game_state == GAME_COOP:
            # Kooperativní mód - hráči proti nepřátelům
            screen.fill(BLACK)
            
            # Aktualizace a vykreslení hráčů
            for player in players:
                player.update()
                if player.alive:
                    player.draw(screen)
            
            # Ovládání 
            for i, player in enumerate(players):
                if player.alive:
                    if player.controls == "keyboard1":
                        # Ovládání klávesnicí pro hráče 1
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_a]:
                            player.move(-player.speed, 0)
                        if keys[pygame.K_d]:
                            player.move(player.speed, 0)
                        if keys[pygame.K_w]:
                            player.move(0, -player.speed)
                        if keys[pygame.K_s]:
                            player.move(0, player.speed)
                        
                        # Střelba
                        if keys[pygame.K_SPACE]:
                            player.shoot(bullets, (0, -1))  # Střelba nahoru
                    
                    elif player.controls == "keyboard2":
                        # Ovládání klávesnicí pro hráče 2
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LEFT]:
                            player.move(-player.speed, 0)
                        if keys[pygame.K_RIGHT]:
                            player.move(player.speed, 0)
                        if keys[pygame.K_UP]:
                            player.move(0, -player.speed)
                        if keys[pygame.K_DOWN]:
                            player.move(0, player.speed)
                        
                        # Střelba
                        if keys[pygame.K_RCTRL] or keys[pygame.K_RETURN]:
                            player.shoot(bullets, (0, -1))  # Střelba nahoru
                    
                    # Ovládání joystickem
                    elif isinstance(player.controls, int) and player.controls < len(joysticks):
                        # Ovládání joystickem
                        joystick = joysticks[player.controls]
                        
                        # Pohyb pomocí levé páčky
                        x_axis = joystick.get_axis(0)
                        y_axis = joystick.get_axis(1)
                        
                        #pohyb, citlivost
                        if abs(x_axis) > 0.1:
                            player.move(x_axis * player.speed, 0)
                        if abs(y_axis) > 0.1:
                            player.move(0, y_axis * player.speed)
                        
                        # Míření pomocí pravé páčky
                        aim_x = joystick.get_axis(2)
                        aim_y = joystick.get_axis(3)
                        
                        # Pokud je páčka vychýlena dostatečně, aktualizujeme směr míření
                        if abs(aim_x) > 0.5 or abs(aim_y) > 0.5:
                            length = math.sqrt(aim_x * aim_x + aim_y * aim_y)
                            player.aim_direction = (aim_x / length, aim_y / length)
                            player.aim_visible = True
                        else:
                            player.aim_visible = False
                        
                        # Střelba pomocí RT
                        if joystick.get_axis(5) > 0.5:  # RT je 5
                            player.shoot(bullets, player.aim_direction)
                        
            
            # Aktualizace střel
            for bullet in bullets[:]:
                bullet.update()
                if bullet.is_off_screen():
                    bullets.remove(bullet)
                else:
                    bullet.draw(screen)
                    
                    # Kontrola kolize s hráči (kromě vlastníka střely)
                    for player in players:
                        if player.alive and player.color != bullet.owner_color:
                            collision_detected = False
                            for point_x, point_y in bullet.trajectory:
                                if (player.x < point_x + bullet.radius and
                                    player.x + player.width > point_x - bullet.radius and
                                    player.y < point_y + bullet.radius and
                                    player.y + player.height > point_y - bullet.radius):
                                    
                                    player.take_damage(25)
                                    if bullet in bullets:
                                        bullets.remove(bullet)
                                    
                                    # Přidání skóre hráči, který vystřelil
                                    for p in players:
                                        if p.color == bullet.owner_color:
                                            p.score += 5
                                            break
                                    
                                    collision_detected = True
                                    break
                            
                            if collision_detected:
                                break

            # Generování powerupů
            powerup_spawn_timer += 1
            if powerup_spawn_timer >= powerup_spawn_delay:
                powerups.append(PowerUp())
                powerup_spawn_timer = 0

            # Aktualizace a vykreslení powerupů
            for powerup in powerups[:]:
                powerup.update()
                powerup.draw(screen)
                
                # Kontrola kolize s hráči
                for player in players:
                    if player.alive and powerup.collides_with(player):
                        player.activate_shield()
                        powerups.remove(powerup)
                        break

            
            # Spawn nepřátel
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= enemy_spawn_delay:
                enemies.append(Enemy())
                enemy_spawn_timer = 0
                # Postupně zrychlujeme spawn nepřátel
                enemy_spawn_delay = max(30, enemy_spawn_delay - 1)
            
            # Aktualizace nepřátel
            for enemy in enemies[:]:
                # Najdi nejbližšího živého hráče
                closest_player = None
                min_distance = float('inf')
                
                for player in players:
                    if player.alive:
                        dx = player.x - enemy.x
                        dy = player.y - enemy.y
                        distance = math.sqrt(dx * dx + dy * dy)
                        
                        if distance < min_distance:
                            min_distance = distance
                            closest_player = player
                
                if closest_player:
                    enemy.move_towards_player(closest_player.x + closest_player.width // 2, 
                                             closest_player.y + closest_player.height // 2)
                
                # Vykreslení nepřítele
                enemy.draw(screen)
                
                # Kontrola kolize s hráči
                for player in players:
                    if player.alive and enemy.collides_with(player.x, player.y, player.width, player.height):
                        player.take_damage(25)
                        enemies.remove(enemy)
                        break
                
                # Kontrola kolize se střelami
                for bullet in bullets[:]:
                    # Kontrola kolize v každém bodu trajektorie střely
                    collision_detected = False
                    for point_x, point_y in bullet.trajectory:
                        if enemy.collides_with(point_x - bullet.radius, point_y - bullet.radius, bullet.radius * 2, bullet.radius * 2):
                            if enemy.take_damage(25):
                                enemies.remove(enemy)
                                # Najdi hráče, kterému patří střela, a přidej mu skóre
                                for player in players:
                                    if player.color == bullet.owner_color:
                                        player.score += 25
                                        break
                            if bullet in bullets:  # Kontrola, zda střela ještě existuje
                                bullets.remove(bullet)
                            collision_detected = True
                            break
                    
                    if collision_detected:
                        break


            
            # Vykreslení skóre a zdraví
            for i, player in enumerate(players):
                draw_text(screen, f"Hráč {i+1}: {player.score}", 36, 150 + i * 300, 30, player.color)
                draw_text(screen, f"HP: {player.health}", 36, 150 + i * 300, 70, player.color)
            
            # Kontrola, zda jsou všichni hráči mrtví
            if all(not player.alive for player in players):
                screen.fill(BLACK)
                # Vykreslení výsledkové tabule
                scoreboard_height = 100
                scoreboard_bg = pygame.Surface((WIDTH, scoreboard_height), pygame.SRCALPHA)
                scoreboard_bg.fill((0, 0, 0, 180))  # Poloprůhledné černé pozadí
                screen.blit(scoreboard_bg, (0, 0))

                # Nadpis výsledkové tabule
                draw_text(screen, "VÝSLEDKOVÁ TABULE", 36, WIDTH // 2, 25, YELLOW)

                # Informace o hráčích
                for i, player in enumerate(players):
                    # Pozice pro informace o hráči
                    x_pos = WIDTH // 4 + i * (WIDTH // 2)
                    
                    # Jméno hráče a skóre
                    draw_text(screen, f"HRÁČ {i+1}", 30, x_pos, 50, player.color)
                    draw_text(screen, f"Skóre: {player.score}", 24, x_pos, 75, WHITE)
                    
                    # Ukazatel zdraví
                    health_width = 150
                    health_height = 15
                    health_x = x_pos - health_width // 2
                    health_y = 90
                    
                    # Pozadí ukazatele zdraví
                    pygame.draw.rect(screen, WHITE, (health_x, health_y, health_width, health_height))
                    
                    # Aktuální zdraví
                    current_health_width = (player.health / player.max_health) * health_width
                    health_color = GREEN
                    if player.health < player.max_health * 0.3:
                        health_color = RED
                    elif player.health < player.max_health * 0.7:
                        health_color = YELLOW
                    pygame.draw.rect(screen, health_color, (health_x, health_y, current_health_width, health_height))
                    
                    # Text zdraví
                    draw_text(screen, f"{player.health}/{player.max_health} HP", 18, x_pos, health_y + health_height // 2, BLACK)
                    
                    # Indikátor štítu
                    if player.shield_active:
                        draw_text(screen, "ŠTÍT AKTIVNÍ", 18, x_pos, health_y + 25, (0, 150, 255))

                
                # Aktualizace a vykreslení položek menu
                mouse_pos = pygame.mouse.get_pos()
                for i, item in enumerate(game_over_items):
                    # Nastavení výběru položky
                    item.is_selected = (i == selected_item)
                    
                    # Kontrola myši
                    if item.check_hover(mouse_pos) and pygame.mouse.get_pressed()[0]:
                        if i == 0:  # Hrát znovu
                            # Restart kooperativního módu
                            players = [
                                Player(WIDTH // 4, HEIGHT // 2, BLUE, 0 if joysticks else "keyboard1"),
                                Player(3 * WIDTH // 4, HEIGHT // 2, GREEN, 1 if len(joysticks) > 1 else "keyboard2")
                            ]
                            bullets = []
                            enemies = []
                            enemy_spawn_timer = 0
                        elif i == 1:  # Menu
                            game_state = MENU
                            selected_item = 0
                    
                    # Vykreslení položky
                    item.draw(screen)
                
                # Kontrola joysticku pro výběr v menu game over
                if joysticks:
                    joystick = joysticks[0]
                    if joystick.get_button(0):  # A tlačítko
                        if selected_item == 0:  # Hrát znovu
                            # Restart kooperativního módu
                            players = [
                                Player(WIDTH // 4, HEIGHT // 2, BLUE, 0 if joysticks else "keyboard1"),
                                Player(3 * WIDTH // 4, HEIGHT // 2, GREEN, 1 if len(joysticks) > 1 else "keyboard2")
                            ]
                            bullets = []
                            enemies = []
                            enemy_spawn_timer = 0
                        elif selected_item == 1:  # Menu
                            game_state = MENU
                            selected_item = 0
        
        elif game_state == GAME_VS:
            # Mód proti sobě - hráči bojují proti sobě
            screen.fill(BLACK)
            
            # Aktualizace a vykreslení hráčů
            for player in players:
                player.update()
                if player.alive:
                    player.draw(screen)
            
            # Ovládání joystickem
            for i, player in enumerate(players):
                if player.alive:
                    if player.controls == "keyboard1":
                        # Ovládání klávesnicí pro hráče 1
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_a]:
                            player.move(-player.speed, 0)
                        if keys[pygame.K_d]:
                            player.move(player.speed, 0)
                        if keys[pygame.K_w]:
                            player.move(0, -player.speed)
                        if keys[pygame.K_s]:
                            player.move(0, player.speed)
                        
                        # Střelba
                        if keys[pygame.K_SPACE]:
                            # Určení směru střelby
                            direction = (0, -1)  # Výchozí směr (nahoru)
                            if keys[pygame.K_a]:
                                direction = (-1, 0)
                            elif keys[pygame.K_d]:
                                direction = (1, 0)
                            elif keys[pygame.K_s]:
                                direction = (0, 1)
                            
                            player.shoot(bullets, direction)
                    
                    elif player.controls == "keyboard2":
                        # Ovládání klávesnicí pro hráče 2
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LEFT]:
                            player.move(-player.speed, 0)
                        if keys[pygame.K_RIGHT]:
                            player.move(player.speed, 0)
                        if keys[pygame.K_UP]:
                            player.move(0, -player.speed)
                        if keys[pygame.K_DOWN]:
                            player.move(0, player.speed)
                        
                        # Střelba
                        if keys[pygame.K_RCTRL] or keys[pygame.K_RETURN]:
                            # Určení směru střelby
                            direction = (0, -1)  # Výchozí směr (nahoru)
                            if keys[pygame.K_LEFT]:
                                direction = (-1, 0)
                            elif keys[pygame.K_RIGHT]:
                                direction = (1, 0)
                            elif keys[pygame.K_DOWN]:
                                direction = (0, 1)
                            
                            player.shoot(bullets, direction)
                    
                    # Ovládání joystickem
                    elif isinstance(player.controls, int) and player.controls < len(joysticks):
                        # Ovládání joystickem
                        joystick = joysticks[player.controls]
                        
                        # Pohyb pomocí levé páčky
                        x_axis = joystick.get_axis(0)
                        y_axis = joystick.get_axis(1)
                        
                        if abs(x_axis) > 0.1:
                            player.move(x_axis * player.speed, 0)
                        if abs(y_axis) > 0.1:
                            player.move(0, y_axis * player.speed)
                        
                        # Míření pomocí pravé páčky
                        aim_x = joystick.get_axis(2)
                        aim_y = joystick.get_axis(3)
                        
                        # Pokud je páčka vychýlena dostatečně, aktualizujeme směr míření
                        if abs(aim_x) > 0.5 or abs(aim_y) > 0.5:
                            length = math.sqrt(aim_x * aim_x + aim_y * aim_y)
                            player.aim_direction = (aim_x / length, aim_y / length)
                            player.aim_visible = True
                        else:
                            player.aim_visible = False
                        
                        # Střelba pomocí RT (tlačítko 7 na Xbox ovladači)
                        if joystick.get_axis(5) > 0.5:  # RT je obvykle osa 5 (může se lišit podle ovladače)
                            player.shoot(bullets, player.aim_direction)
                        
            
            # Aktualizace střel
            for bullet in bullets[:]:
                bullet.update()
                if bullet.is_off_screen():
                    bullets.remove(bullet)
                else:
                    bullet.draw(screen)
                    
                    # Kontrola kolize s hráči (kromě vlastníka střely)
                    for player in players:
                        if player.alive and player.color != bullet.owner_color:
                            collision_detected = False
                            for point_x, point_y in bullet.trajectory:
                                if (player.x < point_x + bullet.radius and
                                    player.x + player.width > point_x - bullet.radius and
                                    player.y < point_y + bullet.radius and
                                    player.y + player.height > point_y - bullet.radius):
                                    
                                    player.take_damage(25)
                                    if bullet in bullets:
                                        bullets.remove(bullet)
                                    
                                    # Přidání skóre hráči, který vystřelil
                                    for p in players:
                                        if p.color == bullet.owner_color:
                                            p.score += 5
                                            break
                                    
                                    collision_detected = True
                                    break
                            
                            if collision_detected:
                                break

            # V herní smyčce pro GAME_COOP a GAME_VS:
            # Generování powerupů
            powerup_spawn_timer += 1
            if powerup_spawn_timer >= powerup_spawn_delay:
                powerups.append(PowerUp())
                powerup_spawn_timer = 0

            # Aktualizace a vykreslení powerupů
            for powerup in powerups[:]:
                powerup.update()
                powerup.draw(screen)
                
                # Kontrola kolize s hráči
                for player in players:
                    if player.alive and powerup.collides_with(player):
                        player.activate_shield()
                        powerups.remove(powerup)
                        break
                    
                    # Kontrola kolize s hráči (kromě vlastníka střely)
                    for player in players:
                        if player.alive and player.color != bullet.owner_color:
                            if (player.x < bullet.x + bullet.radius and
                                player.x + player.width > bullet.x - bullet.radius and
                                player.y < bullet.y + bullet.radius and
                                player.y + player.height > bullet.y - bullet.radius):
                                
                                player.take_damage(25)
                                if bullet in bullets:
                                    bullets.remove(bullet)
                                
                                # Přidání skóre hráči, který vystřelil
                                for p in players:
                                    if p.color == bullet.owner_color:
                                        p.score += 5
                                        break
                                
                                break
            
            # Vykreslení skóre a zdraví
            for i, player in enumerate(players):
                draw_text(screen, f"Hráč {i+1}: {player.score}", 36, 150 + i * 300, 30, player.color)
                draw_text(screen, f"HP: {player.health}", 36, 150 + i * 300, 70, player.color)
            
            # Kontrola vítěze
            alive_players = [p for p in players if p.alive]
            if len(alive_players) <= 1:
                winner = None
                if len(alive_players) == 1:
                    winner = "player1" if alive_players[0].color == BLUE else "player2"
                
                # Vykreslení obrazovky pro game over
                screen.fill(BLACK)
                
                if winner:
                    if winner == "player1":
                        draw_text(screen, f"HRÁČ 1 VYHRÁL!", 72, WIDTH // 2, HEIGHT // 4, BLUE)
                    else:
                        draw_text(screen, "HRÁČ 2 VYHRÁL!", 72, WIDTH // 2, HEIGHT // 4, RED)
                else:
                    draw_text(screen, "REMÍZA", 72, WIDTH // 2, HEIGHT // 4, YELLOW)
                
                # Aktualizace a vykreslení položek menu
                mouse_pos = pygame.mouse.get_pos()
                for i, item in enumerate(game_over_items):
                    # Nastavení výběru položky
                    item.is_selected = (i == selected_item)
                    
                    # Kontrola myši
                    if item.check_hover(mouse_pos) and pygame.mouse.get_pressed()[0]:
                        if i == 0:  # Hrát znovu
                            # Restart módu proti sobě
                            players = [
                                Player(WIDTH // 4, HEIGHT // 2, BLUE, 0 if joysticks else "keyboard1"),
                                Player(3 * WIDTH // 4, HEIGHT // 2, RED, 1 if len(joysticks) > 1 else "keyboard2")
                            ]
                            bullets = []
                        elif i == 1:  # Menu
                            game_state = MENU
                            selected_item = 0
                    
                    # Vykreslení položky
                    item.draw(screen)
                
                # Kontrola joysticku pro výběr v menu game over
                if joysticks:
                    joystick = joysticks[0]
                    if joystick.get_button(0):  # A tlačítko
                        if selected_item == 0:  # Hrát znovu
                            # Restart módu proti sobě
                            players = [
                                Player(WIDTH // 4, HEIGHT // 2, BLUE, 0 if joysticks else "keyboard1"),
                                Player(3 * WIDTH // 4, HEIGHT // 2, RED, 1 if len(joysticks) > 1 else "keyboard2")
                            ]
                            bullets = []
                        elif selected_item == 1:  # Menu
                            game_state = MENU
                            selected_item = 0
        
        elif game_state == PAUSED:
            # Pauza - zobrazení menu pauzy
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Poloprůhledné černé pozadí
            screen.blit(overlay, (0, 0))
            
            draw_text(screen, "PAUZA", 72, WIDTH // 2, HEIGHT // 4)
            
            # Aktualizace a vykreslení položek menu
            mouse_pos = pygame.mouse.get_pos()
            for i, item in enumerate(pause_items):
                # Nastavení výběru položky
                item.is_selected = (i == selected_item)
                
                # Kontrola myši
                if item.check_hover(mouse_pos) and pygame.mouse.get_pressed()[0]:
                    if i == 0:  # Pokračovat
                        game_state = GAME_COOP if len(enemies) > 0 else GAME_VS
                    elif i == 1:  # Menu
                        game_state = MENU
                        selected_item = 0
                    elif i == 2:  # Ukončit
                        running = False
                
                # Vykreslení položky
                item.draw(screen)
        
        # Aktualizace obrazovky
        pygame.display.flip()
        clock.tick(FPS)
        
    
    # Přepnutí zpět do okenního režimu před ukončením
    pygame.display.set_mode((800, 600))
    pygame.quit()
    sys.exit()