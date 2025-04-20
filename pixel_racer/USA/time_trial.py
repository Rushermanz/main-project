# File: pixel_racer/Baku/time_trial.py

import pygame, sys, math, time
import requests
from utils import scale_image

# ======= Load Player Name from current_player.json =======
try:
    with open("current_player.json") as f:
        player_name = f.read().strip()
except:
    player_name = "Player 1"


# ======= Sound Setup =======
pygame.mixer.init()
idle_sound      = pygame.mixer.Sound("assets/idle.wav");      idle_sound.set_volume(1.0); idle_sound.play(loops=-1)
accelerate_sound= pygame.mixer.Sound("assets/accelerate.wav");accelerate_sound.set_volume(0.2)
collision_sound = pygame.mixer.Sound("assets/collision.wav")
drs_sound       = pygame.mixer.Sound("assets/drs.wav")

# ======= Player Car Class =======
class Red_car(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.original_image = scale_image(pygame.image.load('assets/red_car.png').convert_alpha(), 0.9)
        self.image = self.original_image
        self.rect  = self.image.get_rect(center=pos)
        self.mask  = pygame.mask.from_surface(self.image)
        self.pos   = pygame.Vector2(pos)
        self.angle = 255
        self.speed = 0
        self.acceleration   = 0.05
        self.max_speed      =  8
        self.original_max_speed = self.max_speed
        self.deceleration   = 0.06
        self.turn_speed     = 1.5
        self.last_pos       = self.pos.copy()
        self.drs_active     = False

    def input(self):
        keys = pygame.key.get_pressed()
        # block input while countdown or result screen is up
        if countdown_timer > 0 or camera_group.show_result:
            return

        if keys[pygame.K_UP]:
            if self.speed == 0:
                accelerate_sound.play()
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed/2)
        else:
            # natural deceleration
            if self.speed > 0:
                self.speed = max(self.speed - self.deceleration, 0)
            else:
                self.speed = min(self.speed + self.deceleration, 0)

        # steering
        if self.speed != 0:
            turn = self.turn_speed * (1 if self.speed>0 else -1)
            if keys[pygame.K_LEFT]:
                self.angle += turn
            if keys[pygame.K_RIGHT]:
                self.angle -= turn

    def update(self):
        self.input()
        self.last_pos = self.pos.copy()
        rad = math.radians(self.angle)
        direction = pygame.Vector2(math.sin(rad), math.cos(rad)) * -1
        self.pos += direction * self.speed
        self.rect.center = self.pos
        # rotate sprite
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect  = self.image.get_rect(center=self.rect.center)
        self.mask  = pygame.mask.from_surface(self.image)

    def rollback(self):
        self.pos = self.last_pos
        self.rect.center = self.pos
        self.speed = 0
        collision_sound.play()


# ======= Camera + Game Logic =======
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        ds = pygame.display.get_surface()
        self.display_surface = ds
        self.offset = pygame.math.Vector2()
        self.half_w = ds.get_width()  // 2
        self.half_h = ds.get_height() // 2

        # load track, border, DRS & finish line
        self.track_surface  = scale_image(pygame.image.load('assets/usa.png').convert_alpha(), 2.9)
        self.track_rect     = self.track_surface.get_rect(topleft=(0,0))
        self.border_surface = scale_image(pygame.image.load('assets/usa_border.png').convert_alpha(), 2.9)
        self.border_rect    = self.border_surface.get_rect(topleft=(0,0))
        self.border_mask    = pygame.mask.from_surface(self.border_surface)

        self.drs_surface  = scale_image(pygame.image.load('assets/usa_drs.png').convert_alpha(), 2.9)
        self.drs_rect     = self.drs_surface.get_rect(topleft=(0,0))
        self.drs_mask     = pygame.mask.from_surface(self.drs_surface)

        self.finish_img   = pygame.transform.rotate(
            scale_image(pygame.image.load('assets/finish.png').convert_alpha(), 2.4),
            255
        )
        self.finish_rect  = self.finish_img.get_rect(center=(1793, 5755))
        self.finish_mask  = pygame.mask.from_surface(self.finish_img)

        # timer & state
        self.start_time   = 0
        self.lap_time     = 0.0
        self.lap_started  = False
        self.crossed_once = False
        self.recently_crossed = False
        self.show_result  = False

        # minimap
        self.minimap_scale = 0.025
        self.minimap       = pygame.transform.scale(
            self.track_surface,
            (int(self.track_surface.get_width()*self.minimap_scale),
             int(self.track_surface.get_height()*self.minimap_scale))
        )
        self.minimap_rect = self.minimap.get_rect(topleft=(20,70))

    def center_target_camera(self, target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def custom_draw(self, player):
        self.center_target_camera(player)
        self.display_surface.fill((0,100,0))
        # track + border
        self.display_surface.blit(self.track_surface,  self.track_rect.topleft  - self.offset)
        self.display_surface.blit(self.border_surface,self.border_rect.topleft - self.offset)

        # sprites
        for spr in sorted(self.sprites(), key=lambda s: s.rect.centery):
            self.display_surface.blit(spr.image, spr.rect.topleft - self.offset)

        # collision
        off = (int(player.rect.left - self.border_rect.left),
               int(player.rect.top  - self.border_rect.top ))
        if self.border_mask.overlap(player.mask, off):
            player.rollback()

        # DRS
        doff = (int(player.rect.left - self.drs_rect.left),
                int(player.rect.top  - self.drs_rect.top ))
        in_drs = bool(self.drs_mask.overlap(player.mask, doff))
        if in_drs and not player.drs_active:
            drs_sound.play()
        player.drs_active = in_drs
        player.max_speed = player.original_max_speed + 2 if in_drs else player.original_max_speed

        # finish‐line detection
        foff = (int(player.rect.left - self.finish_rect.left),
                int(player.rect.top  - self.finish_rect.top ))
        on_finish = bool(self.finish_mask.overlap(player.mask, foff))

        if on_finish and not self.recently_crossed:
            if not self.crossed_once:
                # start your lap timer
                self.start_time = time.time()
                self.lap_started = True
                self.crossed_once = True
            elif self.lap_started:
                # finish
                self.lap_time    = time.time() - self.start_time
                self.lap_started = False
                self.crossed_once= False
                self.show_result = True

                # immediately POST your result back to your Flask app:
                try:
                    requests.post(
                        'http://127.0.0.1:5000/submit_time',
                        json={
                        'track_id': 5,
                        'lap_time': round(self.lap_time,2),
                        'player_name': player_name
                        },
                        timeout=2
                    )

                except Exception:
                    pass

        self.recently_crossed = on_finish

        # draw finish
        self.display_surface.blit(self.finish_img, self.finish_rect.topleft - self.offset)

        # HUD: timer / speed / minimap / DRS
        if self.lap_started:
            txt = f"Time: {time.time() - self.start_time:.2f}s"
        elif self.lap_time>0:
            txt = f"Final Time: {self.lap_time:.2f}s"
        else:
            txt = "Time: --.--s"

        self.display_surface.blit(font.render(txt, True, (255,255,255)), (20,20))

        # minimap
        pygame.draw.rect(self.display_surface,(255,255,255), self.minimap_rect.inflate(4,4), 2)
        self.display_surface.blit(self.minimap, self.minimap_rect)
        mx = int(player.rect.centerx * self.minimap_scale)
        my = int(player.rect.centery * self.minimap_scale)
        pygame.draw.circle(self.display_surface,(255,0,0),
            (self.minimap_rect.left+mx, self.minimap_rect.top+my), 3)

        # speedometer
        spd = font.render(f"Speed: {player.speed:.1f} px/frame", True, (255,255,255))
        self.display_surface.blit(spd, (20, HEIGHT-40))

        # DRS label
        if in_drs:
            drs_lbl = font.render("DRS ACTIVE", True, (0,255,0))
            self.display_surface.blit(drs_lbl,(WIDTH-180,20))

        # countdown
        if countdown_timer>0:
            cd = font.render(f"{int(countdown_timer)+1}", True, (255,0,0))
            self.display_surface.blit(cd,(WIDTH//2-20, HEIGHT//2-20))

        # result overlay
        if self.show_result:
            overlay = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.display_surface.blit(overlay,(0,0))

            final = font.render(f"Your final time is {self.lap_time:.2f} sec", True, (255,255,255))
            self.display_surface.blit(final,(WIDTH//2-final.get_width()//2,HEIGHT//2-40))

            prompt= font.render("Press ENTER to retry or ESC to exit", True, (200,200,200))
            self.display_surface.blit(prompt,(WIDTH//2-prompt.get_width()//2,HEIGHT//2+10))


# ======= INIT & MAIN LOOP =======
pygame.init()
# play background music inside game
pygame.mixer.music.load("assets/time_trial.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

WIDTH,HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
clock  = pygame.time.Clock()
font   = pygame.font.Font(None,36)
start_ticks = pygame.time.get_ticks()

camera_group = CameraGroup()
player       = Red_car((2004, 5859), camera_group)

while True:
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT or (ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE):
            pygame.quit(); sys.exit()
        # retry on ENTER
        if camera_group.show_result and ev.type==pygame.KEYDOWN and ev.key==pygame.K_RETURN:
            camera_group.show_result   = False
            camera_group.lap_time      = 0
            camera_group.lap_started   = False
            camera_group.crossed_once  = False
            camera_group.recently_crossed = False
            player.pos    = pygame.Vector2(2004, 5859)
            player.rect.center = player.pos
            player.speed  = 0
            player.angle  = 215
            start_ticks   = pygame.time.get_ticks()

    countdown_timer = max(0, 3 - (pygame.time.get_ticks()-start_ticks)/1000)

    camera_group.update()
    camera_group.custom_draw(player)
    pygame.display.update()
    clock.tick(60)
