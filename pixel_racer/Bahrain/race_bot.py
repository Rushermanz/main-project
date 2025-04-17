# File: pixel_racer/Bahrain/race_bot.py

import pygame, sys, math, time
from utils import scale_image

# ========== Initialize Sound ========== #
pygame.mixer.init()
idle_sound = pygame.mixer.Sound("assets/idle.wav"); idle_sound.set_volume(1.0); idle_sound.play(loops=-1)
accelerate_sound = pygame.mixer.Sound("assets/accelerate.wav"); accelerate_sound.set_volume(0.2)
collision_sound = pygame.mixer.Sound("assets/collision.wav")
drs_sound = pygame.mixer.Sound("assets/drs.wav")

# ========== Car Base Class ========== #
class Car(pygame.sprite.Sprite):
    def __init__(self, pos, group, image_path, angle=90):
        super().__init__(group)
        self.original_image = scale_image(pygame.image.load(image_path).convert_alpha(), 0.9)
        self.image = self.original_image
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
        self.current_wp = 0

    def move(self):
        self.last_pos = self.pos.copy()
        rad = math.radians(self.angle)
        direction = pygame.Vector2(math.sin(rad), math.cos(rad)) * -1
        self.pos += direction * self.speed
        self.rect.center = self.pos
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def rollback(self):
        self.pos = self.last_pos
        self.rect.center = self.pos
        self.speed = 0

# ========== Player & Bot ========== #
class PlayerCar(Car):
    def __init__(self, pos, group):
        super().__init__(pos, group, "assets/red_car.png")

    def update(self):
        keys = pygame.key.get_pressed()
        if countdown_timer > 0 or camera_group.show_result: return
        if keys[pygame.K_UP]:
            if self.speed == 0: accelerate_sound.play()
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed / 2)
        else:
            self.speed += self.deceleration if self.speed < 0 else -self.deceleration
            self.speed = max(min(self.speed, self.max_speed), -self.max_speed/2)
        if self.speed != 0:
            turn = self.turn_speed * (1 if self.speed > 0 else -1)
            if keys[pygame.K_LEFT]: self.angle += turn
            if keys[pygame.K_RIGHT]: self.angle -= turn
        self.move()

    def rollback(self):
        super().rollback()
        collision_sound.play()

class BotCar(Car):
    def __init__(self, pos, group, img, waypoints):
        super().__init__(pos, group, img)
        self.waypoints = waypoints
        self.current_wp = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        if countdown_timer > 0 or camera_group.show_result: return
        if self.current_wp >= len(self.waypoints): return
        target = self.waypoints[self.current_wp]
        vec = pygame.Vector2(target) - self.pos
        angle_to = math.degrees(math.atan2(-vec.y, vec.x)) - 90
        diff = (angle_to - self.angle + 180) % 360 - 180
        self.angle += min(max(diff, -self.turn_speed), self.turn_speed)
        self.speed = min(self.speed + self.acceleration, self.max_speed)
        if vec.length() < 80:
            self.current_wp += 1
        self.move()

    def avoid_collision(self, others):
        for other in others:
            if other != self and pygame.sprite.collide_mask(self, other):
                self.rollback()

# ========== Ranking Logic ========== #
def get_race_positions(cars):
    def progress(c):
        wp = min(c.current_wp, len(bot1.waypoints)-1)
        dist = pygame.Vector2(bot1.waypoints[wp]).distance_to(c.pos)
        return wp - dist / 1000  # closer = higher
    return sorted(cars, key=progress, reverse=True)

# ========== Camera Group ========== #
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        self.track_surface = scale_image(pygame.image.load("assets/bahrain.png").convert_alpha(), 2.7)
        self.border_surface = scale_image(pygame.image.load("assets/bahrain_border.png").convert_alpha(), 2.7)
        self.drs_surface = scale_image(pygame.image.load("assets/bahrain_drs.png").convert_alpha(), 2.7)
        self.finish_img = pygame.transform.rotate(scale_image(pygame.image.load("assets/finish.png").convert_alpha(), 1.9), 90)
        self.border_mask = pygame.mask.from_surface(self.border_surface)
        self.drs_mask = pygame.mask.from_surface(self.drs_surface)
        self.finish_mask = pygame.mask.from_surface(self.finish_img)
        self.track_rect = self.track_surface.get_rect(topleft=(0,0))
        self.border_rect = self.border_surface.get_rect(topleft=(0,0))
        self.drs_rect = self.drs_surface.get_rect(topleft=(0,0))
        self.finish_rect = self.finish_img.get_rect(center=(4657,4083))
        self.half_w = self.display_surface.get_width() // 2
        self.half_h = self.display_surface.get_height() // 2
        self.minimap_scale = 0.025
        self.minimap = pygame.transform.scale(self.track_surface, (int(self.track_surface.get_width()*self.minimap_scale), int(self.track_surface.get_height()*self.minimap_scale)))
        self.minimap_rect = self.minimap.get_rect(topleft=(20,70))
        self.start_time = 0
        self.lap_started = False
        self.crossed_once = False
        self.recently_crossed = False
        self.current_lap = 1
        self.total_laps = 3
        self.lap_times = []
        self.show_result = False

    def center_target_camera(self, target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def custom_draw(self, player, bots):
        self.center_target_camera(player)
        self.display_surface.fill((0,100,0))
        self.display_surface.blit(self.track_surface, self.track_rect.topleft - self.offset)
        self.display_surface.blit(self.border_surface, self.border_rect.topleft - self.offset)
        for spr in sorted(self.sprites(), key=lambda s: s.rect.centery):
            self.display_surface.blit(spr.image, spr.rect.topleft - self.offset)

        for c in [player] + bots:
            off = (int(c.rect.left - self.border_rect.left), int(c.rect.top - self.border_rect.top))
            if self.border_mask.overlap(c.mask, off): c.rollback()
        for bot in bots: bot.avoid_collision([player]+bots)

        # DRS
        doff = (int(player.rect.left - self.drs_rect.left), int(player.rect.top - self.drs_rect.top))
        in_drs = bool(self.drs_mask.overlap(player.mask, doff))
        if in_drs and not player.drs_active: drs_sound.play()
        player.drs_active = in_drs
        player.max_speed = player.original_max_speed + 2 if in_drs else player.original_max_speed

        # Finish Line
        foff = (int(player.rect.left - self.finish_rect.left), int(player.rect.top - self.finish_rect.top))
        if self.finish_mask.overlap(player.mask, foff):
            if not self.recently_crossed:
                if not self.crossed_once:
                    self.crossed_once = True
                elif self.lap_started:
                    duration = time.time() - self.start_time
                    self.lap_times.append(round(duration, 2))
                    self.current_lap += 1
                    if self.current_lap > self.total_laps:
                        self.lap_started = False
                        self.show_result = True
                    else:
                        self.start_time = time.time()
        self.recently_crossed = bool(self.finish_mask.overlap(player.mask, foff))
        self.display_surface.blit(self.finish_img, self.finish_rect.topleft - self.offset)

        # HUD
        timer = f"Time: {time.time()-self.start_time:.2f}s" if self.lap_started else "--.--s"
        self.display_surface.blit(font.render(timer, True, (255,255,255)), (20,20))
        self.display_surface.blit(font.render(f"Lap: {self.current_lap}/{self.total_laps}", True, (255,255,255)), (WIDTH-220, 60))
        self.display_surface.blit(font.render(f"Speed: {player.speed:.1f} px/frame", True, (255,255,255)), (20, HEIGHT-40))
        if in_drs:
            self.display_surface.blit(font.render("DRS ACTIVE", True, (0,255,0)), (WIDTH-180, 20))

        # Minimap
        pygame.draw.rect(self.display_surface, (255,255,255), self.minimap_rect.inflate(4,4), 2)
        self.display_surface.blit(self.minimap, self.minimap_rect)
        mx = int(player.rect.centerx * self.minimap_scale)
        my = int(player.rect.centery * self.minimap_scale)
        pygame.draw.circle(self.display_surface, (255,0,0), (self.minimap_rect.left+mx, self.minimap_rect.top+my), 3)

        # Race Position
        all_cars = [player] + bots
        pos = get_race_positions(all_cars).index(player) + 1
        self.display_surface.blit(font.render(f"Position: {pos}/{len(all_cars)}", True, (255,255,0)), (WIDTH-220, HEIGHT-40))

        # Countdown / GO!
        if countdown_timer > 0:
            cd = font.render(f"{int(countdown_timer)+1}", True, (255,0,0))
            self.display_surface.blit(cd, (WIDTH//2-20, HEIGHT//2-20))
        elif show_go and not self.show_result:
            go = font.render("GO!", True, (0,255,0))
            self.display_surface.blit(go, (WIDTH//2 - go.get_width()//2, HEIGHT//2 - 50))

        # Result screen
        if self.show_result:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.display_surface.blit(overlay, (0,0))
            self.display_surface.blit(font.render("RACE COMPLETE!", True, (255,255,255)), (WIDTH//2-100, 80))
            for i, lap_time in enumerate(self.lap_times):
                self.display_surface.blit(font.render(f"Lap {i+1}: {lap_time:.2f}s", True, (200,200,200)), (WIDTH//2 - 80, 140 + i*40))
            self.display_surface.blit(font.render("Press ENTER to retry or ESC to exit", True, (255,255,0)), (WIDTH//2-170, HEIGHT-100))

# ========== Init ========== #
pygame.init()
pygame.mixer.music.load("assets/easy.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
start_ticks = pygame.time.get_ticks()

camera_group = CameraGroup()
player = PlayerCar((4204, 4135), camera_group)
bot1 = BotCar((3760, 4028), camera_group, "assets/purple_car.png", [(4200, 3900), (4600, 3800), (4800, 4200), (4000, 4400), (3600, 4000), (3760, 4028)])
bot2 = BotCar((3915, 4137), camera_group, "assets/grey_car.png",   [(4200, 3920), (4600, 3830), (4800, 4180), (4000, 4420), (3600, 4020), (3760, 4028)])
bot3 = BotCar((4050, 4033), camera_group, "assets/white_car.png",  [(4200, 3950), (4600, 3850), (4800, 4160), (4000, 4430), (3600, 4030), (3760, 4028)])
bots = [bot1, bot2, bot3]
camera_group.add(player, *bots)

# ========== Main Loop ========== #
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            pygame.quit(); sys.exit()
        if camera_group.show_result and e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
            player.pos = pygame.Vector2(4204, 4135); player.angle = 90; player.speed = 0
            for bot in bots:
                bot.current_wp = 0; bot.speed = 0; bot.pos = pygame.Vector2(bot.rect.center); bot.angle = 90
            camera_group.current_lap = 1
            camera_group.lap_times = []
            camera_group.lap_started = False
            camera_group.crossed_once = False
            camera_group.recently_crossed = False
            camera_group.show_result = False
            start_ticks = pygame.time.get_ticks()

    elapsed = (pygame.time.get_ticks() - start_ticks) / 1000
    countdown_timer = max(0, 3 - elapsed)
    show_go = 0 < elapsed - 3 < 1

    if countdown_timer <= 0 and not camera_group.lap_started and not camera_group.show_result:
        camera_group.start_time = time.time()
        camera_group.lap_started = True
        camera_group.crossed_once = True

    camera_group.update()
    camera_group.custom_draw(player, bots)
    pygame.display.update()
    clock.tick(60)
