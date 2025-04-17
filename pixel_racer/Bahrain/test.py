import pygame, sys, math, time
from utils import scale_image

pygame.mixer.init()

# ======= Load Sound Effects =======
idle_sound = pygame.mixer.Sound("assets/idle.wav")
idle_sound.set_volume(0.0)  # back to normal volume
idle_sound.play(loops=-1)

accelerate_sound = pygame.mixer.Sound("assets/accelerate.wav")
accelerate_sound.set_volume(0.0)  # reduced volume

collision_sound = pygame.mixer.Sound("assets/collision.wav")
drs_sound = pygame.mixer.Sound("assets/drs.wav")


# ======= Track Class =======
class Track(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = scale_image(pygame.image.load('assets/bahrain.png').convert_alpha(), 2.7)
        self.rect = self.image.get_rect(topleft=pos)

# ======= Player Car Class =======
class Red_car(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.original_image = scale_image(pygame.image.load('assets/red_car.png').convert_alpha(), 0.9)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = pygame.Vector2(pos)
        self.angle = 90
        self.speed = 0
        self.acceleration = 0.05
        self.max_speed = 8
        self.original_max_speed = self.max_speed
        self.deceleration = 0.06
        self.turn_speed = 1.5
        self.last_pos = self.pos.copy()
        self.collision_count = 0
        self.drs_active = False
        self.prev_drs_state = False

    def input(self):
        keys = pygame.key.get_pressed()
        if countdown_timer > 0:
            return

        if keys[pygame.K_UP]:
            if self.speed == 0:
                accelerate_sound.play()
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed / 2)
        else:
            if self.speed > 0:
                self.speed = max(self.speed - self.deceleration, 0)
            elif self.speed < 0:
                self.speed = min(self.speed + self.deceleration, 0)

        if self.speed != 0:
            if keys[pygame.K_LEFT]:
                self.angle += self.turn_speed * (1 if self.speed > 0 else -1)
            if keys[pygame.K_RIGHT]:
                self.angle -= self.turn_speed * (1 if self.speed > 0 else -1)

    def update(self):
        self.input()
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
        collision_sound.play()


# ======= Camera Group =======
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_width() // 2
        self.half_h = self.display_surface.get_height() // 2
        self.recently_crossed = False

        self.track_surface = scale_image(pygame.image.load('assets/bahrain.png').convert_alpha(), 2.7)
        self.track_rect = self.track_surface.get_rect(topleft=(0, 0))
        self.border_surface = scale_image(pygame.image.load('assets/bahrain_border.png').convert_alpha(), 2.7)
        self.border_rect = self.border_surface.get_rect(topleft=(0, 0))
        self.border_mask = pygame.mask.from_surface(self.border_surface)

        self.drs_surface = scale_image(pygame.image.load('assets/bahrain_drs.png').convert_alpha(), 2.7)
        self.drs_rect = self.drs_surface.get_rect(topleft=(0, 0))
        self.drs_mask = pygame.mask.from_surface(self.drs_surface)

        self.finish_img = pygame.transform.rotate(
            scale_image(pygame.image.load('assets/finish.png').convert_alpha(), 1.9), 90
        )
        self.finish_rect = self.finish_img.get_rect(center=(4657, 4083))
        self.finish_mask = pygame.mask.from_surface(self.finish_img)

        self.start_time = 0
        self.lap_time = 0
        self.lap_started = False
        self.crossed_once = False

        self.minimap_scale = 0.025
        self.minimap = pygame.transform.scale(self.track_surface, (
            int(self.track_surface.get_width() * self.minimap_scale),
            int(self.track_surface.get_height() * self.minimap_scale)
        ))
        self.minimap_rect = self.minimap.get_rect(topleft=(20, 70))

    def center_target_camera(self, target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def custom_draw(self, player):
        self.center_target_camera(player)
        self.display_surface.fill((0, 100, 0))
        self.display_surface.blit(self.track_surface, self.track_rect.topleft - self.offset)
        self.display_surface.blit(self.border_surface, self.border_rect.topleft - self.offset)

        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

        car_offset = (int(player.rect.left - self.border_rect.left), int(player.rect.top - self.border_rect.top))
        if self.border_mask.overlap(player.mask, car_offset):
            player.rollback()

        drs_offset = (int(player.rect.left - self.drs_rect.left), int(player.rect.top - self.drs_rect.top))
        in_drs = self.drs_mask.overlap(player.mask, drs_offset)

        if in_drs and not player.drs_active:
            drs_sound.play()
        player.drs_active = in_drs
        player.max_speed = player.original_max_speed + 2 if in_drs else player.original_max_speed

        finish_offset = (int(player.rect.left - self.finish_rect.left), int(player.rect.top - self.finish_rect.top))
        on_finish = self.finish_mask.overlap(player.mask, finish_offset)

        if on_finish and not self.recently_crossed:
            if not self.crossed_once:
                self.start_time = time.time()
                self.lap_started = True
                self.crossed_once = True
                print("Timer Started")
            elif self.lap_started:
                self.lap_time = time.time() - self.start_time
                self.lap_started = False
                self.crossed_once = False
                print("Timer Stopped")
            self.recently_crossed = True
        elif not on_finish:
            self.recently_crossed = False

        self.display_surface.blit(self.finish_img, self.finish_rect.topleft - self.offset)

        coord_text = font.render(f"Pos: ({int(player.rect.centerx)}, {int(player.rect.centery)})", True, (255, 255, 255))
        self.display_surface.blit(coord_text, (20, 20))

        if self.lap_started:
            timer_text = font.render(f"Lap Time: {time.time() - self.start_time:.2f}s", True, (255, 255, 255))
        elif self.lap_time > 0:
            timer_text = font.render(f"Final Time: {self.lap_time:.2f}s", True, (255, 255, 0))
        else:
            timer_text = font.render("Lap Time: --.--s", True, (200, 200, 200))
        self.display_surface.blit(timer_text, (20, 60))

        pygame.draw.rect(self.display_surface, (255, 255, 255), self.minimap_rect.inflate(4, 4), 2)
        self.display_surface.blit(self.minimap, self.minimap_rect)
        mini_x = int(player.rect.centerx * self.minimap_scale)
        mini_y = int(player.rect.centery * self.minimap_scale)
        dot_pos = (self.minimap_rect.left + mini_x, self.minimap_rect.top + mini_y)
        pygame.draw.circle(self.display_surface, (255, 0, 0), dot_pos, 3)

        speed_text = font.render(f"Speed: {player.speed:.1f} px/frame", True, (255, 255, 255))
        self.display_surface.blit(speed_text, (20, HEIGHT - 40))

        if in_drs:
            drs_text = font.render("DRS ACTIVE", True, (0, 255, 0))
            self.display_surface.blit(drs_text, (WIDTH - 180, 20))

        if countdown_timer > 0:
            countdown_text = font.render(f"{int(countdown_timer) + 1}", True, (255, 0, 0))
            self.display_surface.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 20))

# ======= Init =======
pygame.init()

pygame.mixer.music.load("assets/time_trial.mp3")  # make sure the file exists in /assets
pygame.mixer.music.set_volume(0.0)
pygame.mixer.music.play(-1)

WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
start_ticks = pygame.time.get_ticks()

camera_group = CameraGroup()
player = Red_car((3760, 4028), camera_group)

# ======= Game Loop =======
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

    countdown_timer = max(0, 3 - (pygame.time.get_ticks() - start_ticks) / 1000)

    camera_group.update()
    camera_group.custom_draw(player)
    pygame.display.update()
    clock.tick(60)
