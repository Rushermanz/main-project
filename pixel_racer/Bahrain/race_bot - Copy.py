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
        super().__init__(pos, group, "assets/red_car.png", angle=90)
        # Force correct orientation on spawn
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)


    def update(self):
        keys = pygame.key.get_pressed()
        if countdown_timer > 0 or camera_group.show_result: return
        if keys[pygame.K_UP]:
            if self.speed == 0: accelerate_sound.play()
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed / 2)
        else:
            if abs(self.speed) < self.deceleration:
                self.speed = 0  # snap to zero to avoid drift
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
    def __init__(self, pos, group, img, waypoints, total_laps=3):
        super().__init__(pos, group, img)
        self.waypoints = waypoints
        self.current_wp = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.lap_count = 1
        self.total_laps = total_laps
          # slightly slower than player

    def update(self):
        if countdown_timer > 0 or camera_group.show_result:
            return

        current_target = pygame.Vector2(self.waypoints[self.current_wp])
        next_idx = (self.current_wp + 1) % len(self.waypoints)
        after_next_idx = (self.current_wp + 2) % len(self.waypoints)
        next_target = pygame.Vector2(self.waypoints[next_idx])
        after_next = pygame.Vector2(self.waypoints[after_next_idx])

        # --- Steering ---
        to_target = current_target - self.pos
        desired_angle = math.degrees(math.atan2(-to_target.y, to_target.x)) - 90
        angle_diff = (desired_angle - self.angle + 180) % 360 - 180
        self.angle += max(min(angle_diff, self.turn_speed), -self.turn_speed)

        # --- Curve Prediction ---
        vec1 = next_target - current_target
        vec2 = after_next - next_target
        curve_angle = abs(vec1.angle_to(vec2))
        alignment_penalty = abs(angle_diff)

        # --- STRAIGHT BOOST LOGIC ---
        if curve_angle < 10 and alignment_penalty < 10:
            target_speed = 10.0   # Max straight speed
            acceleration = 0.15   # Rapid acceleration on straights
        elif curve_angle < 25 and alignment_penalty < 15:
            target_speed = 8.0
            acceleration = 0.09
        elif curve_angle > 100 or alignment_penalty > 90:
            target_speed = 2.5
            acceleration = 0.035
        elif curve_angle > 60 or alignment_penalty > 60:
            target_speed = 4.0
            acceleration = 0.045
        elif curve_angle > 30 or alignment_penalty > 45:
            target_speed = 6.0
            acceleration = 0.055
        else:
            target_speed = self.max_speed + 1.5
            acceleration = 0.07

        # --- Acceleration / Deceleration ---
        if self.speed < target_speed:
            self.speed = min(self.speed + acceleration, target_speed)
        else:
            self.speed = max(self.speed - self.deceleration, target_speed)

        self.move()

        # --- Waypoint Advance ---
        if to_target.length() < 70:
            self.current_wp = (self.current_wp + 1) % len(self.waypoints)
            if self.current_wp == 0:
                self.lap_count += 1







        # Advance Waypoint if Close Enough
        if (current_target - self.pos).length() < 70:
            self.current_wp = (self.current_wp + 1) % len(self.waypoints)
            if self.current_wp == 0:
                self.lap_count += 1




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
        # for bot in bots: bot.avoid_collision([player]+bots)

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
bot1 = BotCar((3760, 4028), camera_group, "assets/purple_car.png", [(2145,4063), (599,4121), (371,4012), (527,3802), (673,3631), (571,3361), (548,2935), (842,604), (971,399), (1252,521), (1642,960), (2120,1290), (2379,1496), (2322,1948), (2916,2447), (3258,2772), (3099,2881), (2499,2760), (1618,2684), (1260,2914), (1285,3066), (1718,3102), (3083,3125), (4376,3121), (4629,2959), (4574,2667), (4144,2288), (3640,2016), (3517,1580), (3691,1101), (3942,735), (4154,700), (4330,906), (5551,2898), (6010,3646), (6100,3867), (5749,4059), (4761,4076)])
#bot2 = BotCar((3915, 4137), camera_group, "assets/grey_car.png",   [(3094,4035), (1896,4076), (861,4088), (451,4059), (373,3961), (512,3813), (666,3684), (583,3373), (568,2883), (600,2268), (743,1139), (825,646), (959,384), (1265,499), (1588,912), (1925,1209), (2255,1382), (2332,1558), (2325,1838), (2470,2111), (2875,2428), (3135,2625), (3256,2776), (3137,2891), (2695,2785), (1975,2704), (1436,2730), (1250,2944), (1362,3107), (1663,3116), (2548,3129), (3397,3131), (4267,3147), (4553,3094), (4601,2848), (4517,2596), (4237,2350), (3820,2160), (3590,1962), (3540,1494), (3743,1013), (3941,752), (4111,694), (4247,826), (4465,1136), (4740,1596), (5026,2070), (5444,2731), (5940,3562), (6096,3782), (6016,3960), (5763,4073), (5309,4083), (4407,4081), (3629,4099)])
#bot3 = BotCar((4050, 4033), camera_group, "assets/white_car.png",  [(3094,4035), (1896,4076), (861,4088), (451,4059), (373,3961), (512,3813), (666,3684), (583,3373), (568,2883), (600,2268), (743,1139), (825,646), (959,384), (1265,499), (1588,912), (1925,1209), (2255,1382), (2332,1558), (2325,1838), (2470,2111), (2875,2428), (3135,2625), (3256,2776), (3137,2891), (2695,2785), (1975,2704), (1436,2730), (1250,2944), (1362,3107), (1663,3116), (2548,3129), (3397,3131), (4267,3147), (4553,3094), (4601,2848), (4517,2596), (4237,2350), (3820,2160), (3590,1962), (3540,1494), (3743,1013), (3941,752), (4111,694), (4247,826), (4465,1136), (4740,1596), (5026,2070), (5444,2731), (5940,3562), (6096,3782), (6016,3960), (5763,4073), (5309,4083), (4407,4081), (3629,4099)])
bots = [bot1,]
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
