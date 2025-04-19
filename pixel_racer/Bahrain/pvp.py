# File: pixel_racer/Bahrain/pvp.py

import pygame, sys, math, time
from utils import scale_image

# Initialize Sound
pygame.mixer.init()
idle_sound = pygame.mixer.Sound("assets/idle.wav"); idle_sound.set_volume(1.0); idle_sound.play(loops=-1)
accelerate_sound = pygame.mixer.Sound("assets/accelerate.wav"); accelerate_sound.set_volume(0.2)
collision_sound = pygame.mixer.Sound("assets/collision.wav")
drs_sound = pygame.mixer.Sound("assets/drs.wav")

# Car Class
class Car(pygame.sprite.Sprite):
    def __init__(self, pos, image_path, controls, angle=90):
        super().__init__()
        self.original_image = scale_image(pygame.image.load(image_path).convert_alpha(), 0.9)
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = pygame.Vector2(pos)
        self.angle = angle
        self.speed = 0
        self.acceleration = 0.05
        self.max_speed = 8
        self.original_max_speed = self.max_speed
        self.deceleration = 0.06
        self.turn_speed = 1.5
        self.last_pos = self.pos.copy()
        self.drs_active = False
        self.controls = controls
        self.lap_count = 1
        self.finished = False
        self.recently_crossed = False
        self.lap_times = []
        self.last_lap_time = None

    def move(self):
        self.last_pos = self.pos.copy()
        rad = math.radians(self.angle)
        direction = pygame.Vector2(math.sin(rad), math.cos(rad)) * -1
        self.pos += direction * self.speed
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        keys = pygame.key.get_pressed()
        if countdown_timer > 0 or show_result or self.finished:
            return
        if keys[self.controls["up"]]:
            if self.speed == 0: accelerate_sound.play()
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[self.controls["down"]]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed / 2)
        else:
            if abs(self.speed) < self.deceleration:
                self.speed = 0
            else:
                self.speed += self.deceleration if self.speed < 0 else -self.deceleration
        self.speed = max(min(self.speed, self.max_speed), -self.max_speed/2)
        if self.speed != 0:
            turn = self.turn_speed * (1 if self.speed > 0 else -1)
            if keys[self.controls["left"]]: self.angle += turn
            if keys[self.controls["right"]]: self.angle -= turn
        self.move()

    def rollback(self):
        self.pos = self.last_pos
        self.rect.center = self.pos
        self.speed = 0
        collision_sound.play()

# Controls
P1_CONTROLS = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d}
P2_CONTROLS = {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT}

# Camera Draw
def draw_camera(surface, player, opponent, font):
    offset = pygame.Vector2(player.rect.centerx - surface.get_width() // 2,
                            player.rect.centery - surface.get_height() // 2)

    surface.fill((0, 100, 0))
    surface.blit(track_surface, track_rect.topleft - offset)
    surface.blit(border_surface, border_rect.topleft - offset)

    for car in [player, opponent]:
        off = (int(car.rect.left - border_rect.left), int(car.rect.top - border_rect.top))
        if border_mask.overlap(car.mask, off):
            car.rollback()

        # DRS
        doff = (int(car.rect.left - drs_rect.left), int(car.rect.top - drs_rect.top))
        in_drs = bool(drs_mask.overlap(car.mask, doff))
        if in_drs and not car.drs_active:
            drs_sound.play()
        car.drs_active = in_drs
        car.max_speed = car.original_max_speed + 2 if in_drs else car.original_max_speed

        # Finish Line
        foff = (int(car.rect.left - finish_rect.left), int(car.rect.top - finish_rect.top))
        if finish_mask.overlap(car.mask, foff):
            if not car.recently_crossed:
                now = time.time()
                if car.last_lap_time is not None:
                    car.lap_times.append(round(now - car.last_lap_time, 2))
                car.last_lap_time = now
                car.lap_count += 1
                if car.lap_count > 3:
                    car.finished = True
                car.recently_crossed = True
        else:
            car.recently_crossed = False

        surface.blit(car.image, car.rect.topleft - offset)

    surface.blit(finish_img, finish_rect.topleft - offset)
    surface.blit(font.render(f"Laps: {player.lap_count}/3", True, (255,255,255)), (20, 20))
    surface.blit(font.render(f"Speed: {player.speed:.1f}", True, (255,255,255)), (20, 50))
    if player.drs_active:
        surface.blit(font.render("DRS ACTIVE", True, (0,255,0)), (20, 80))

# Init
pygame.init()
pygame.mixer.music.load("assets/easy.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
start_ticks = pygame.time.get_ticks()

# Assets
track_surface = scale_image(pygame.image.load("assets/bahrain.png").convert_alpha(), 2.7)
border_surface = scale_image(pygame.image.load("assets/bahrain_border.png").convert_alpha(), 2.7)
drs_surface = scale_image(pygame.image.load("assets/bahrain_drs.png").convert_alpha(), 2.7)
finish_img = pygame.transform.rotate(scale_image(pygame.image.load("assets/finish.png").convert_alpha(), 1.9), 90)

border_mask = pygame.mask.from_surface(border_surface)
drs_mask = pygame.mask.from_surface(drs_surface)
finish_mask = pygame.mask.from_surface(finish_img)

track_rect = track_surface.get_rect(topleft=(0,0))
border_rect = border_surface.get_rect(topleft=(0,0))
drs_rect = drs_surface.get_rect(topleft=(0,0))
finish_rect = finish_img.get_rect(center=(4657,4083))

# Players
player1 = Car((4204, 4135), "assets/red_car.png", P1_CONTROLS)
player2 = Car((4050, 4033), "assets/white_car.png", P2_CONTROLS)

# Split-screen surfaces
p1_surface = pygame.Surface((WIDTH // 2, HEIGHT))
p2_surface = pygame.Surface((WIDTH // 2, HEIGHT))

# Game loop
show_result = False
winner = None

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            pygame.quit(); sys.exit()
        if show_result and e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
            for car, pos in zip([player1, player2], [(4204, 4135), (4050, 4033)]):
                car.pos = pygame.Vector2(pos)
                car.rect.center = pos
                car.speed = 0
                car.angle = 90
                car.lap_count = 1
                car.finished = False
                car.lap_times = []
                car.last_lap_time = None
            show_result = False
            winner = None
            start_ticks = pygame.time.get_ticks()

    elapsed = (pygame.time.get_ticks() - start_ticks) / 1000
    countdown_timer = max(0, 3 - elapsed)

    if countdown_timer <= 0 and not player1.last_lap_time:
        player1.last_lap_time = time.time()
        player2.last_lap_time = time.time()

    if countdown_timer <= 0 and not show_result:
        player1.update()
        player2.update()

    if player1.finished and player2.finished and not show_result:
        show_result = True
        winner = "PLAYER 1" if player1.lap_count > player2.lap_count else "PLAYER 2"

    draw_camera(p1_surface, player1, player2, font)
    draw_camera(p2_surface, player2, player1, font)

    screen.blit(p1_surface, (0, 0))
    screen.blit(p2_surface, (WIDTH // 2, 0))

    if show_result:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        screen.blit(overlay, (0,0))

        title = font.render("RACE COMPLETE", True, (255,255,255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))

        winner_label = font.render(f"{winner} WINS!", True, (255,255,0))
        screen.blit(winner_label, (WIDTH//2 - winner_label.get_width()//2, 120))

        # Player 1 lap times
        screen.blit(font.render("P1 Laps:", True, (255,0,0)), (WIDTH//2 - 300, 180))
        for i, t in enumerate(player1.lap_times):
            screen.blit(font.render(f"Lap {i+1}: {t}s", True, (255,0,0)), (WIDTH//2 - 300, 210 + i*30))

        # Player 2 lap times
        screen.blit(font.render("P2 Laps:", True, (0,0,255)), (WIDTH//2 + 100, 180))
        for i, t in enumerate(player2.lap_times):
            screen.blit(font.render(f"Lap {i+1}: {t}s", True, (0,0,255)), (WIDTH//2 + 100, 210 + i*30))

        prompt = font.render("Press ENTER to restart or ESC to quit", True, (255,255,255))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT - 80))
        # Countdown / GO display (overlay)
    if countdown_timer > 0:
        cd_text = font.render(str(int(countdown_timer) + 1), True, (255, 255, 255))
        screen.blit(cd_text, (WIDTH // 2 - cd_text.get_width() // 2, HEIGHT // 2 - 80))
    elif 0 < elapsed - 3 < 1:
        go_text = font.render("GO!", True, (0, 255, 0))
        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 80))

    pygame.display.update()
    clock.tick(60)
