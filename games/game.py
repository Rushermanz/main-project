import pygame, sys, math
from utils import scale_image

# ========== Track Sprite (Optional group logic kept) ==========
class Track(pygame.sprite.Sprite): 
    def __init__(self, pos , group):
        super().__init__(group)
        self.image = scale_image(pygame.image.load('assets/usa.png').convert_alpha(), 5.7)
        self.rect = self.image.get_rect(topleft=pos)

# ========== Player Car Class ==========
class Red_car(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.original_image = scale_image(pygame.image.load('assets/red_car.png').convert_alpha(), 0.9)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.Vector2(pos)
        self.angle = 0
        self.speed = 0
        self.acceleration = 0.1
        self.max_speed = 10.0
        self.deceleration = 0.1
        self.turn_speed = 0.9
        self.last_pos = self.pos.copy()

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
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

# ========== Camera Group Class ==========
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_width() // 2
        self.half_h = self.display_surface.get_height() // 2

        self.track_surface = scale_image(pygame.image.load('assets/usa.png').convert_alpha(), 5.7)
        self.track_rect = self.track_surface.get_rect(topleft=(0, 0))

        self.border_surface = scale_image(pygame.image.load('assets/usa_border.png').convert_alpha(), 5.7)
        self.border_rect = self.border_surface.get_rect(topleft=(0, 0))
        self.border_mask = pygame.mask.from_surface(self.border_surface)

    def center_target_camera(self, target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def custom_draw(self, player):
        self.center_target_camera(player)

        # Clear the screen
        self.display_surface.fill((0, 100, 0))

        # Draw track and border with camera offset
        track_offset = self.track_rect.topleft - self.offset
        border_offset = self.border_rect.topleft - self.offset
        self.display_surface.blit(self.track_surface, track_offset)
        self.display_surface.blit(self.border_surface, border_offset)

        # Draw sprites (car)
        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

        # Collision Detection
        car_offset = (int(player.rect.left - self.border_rect.left),
                      int(player.rect.top - self.border_rect.top))

        if self.border_mask.overlap(player.mask, car_offset):
            print("COLLISION!")
            player.rollback()

        # Coordinates Display
        coord_text = font.render(f"Pos: ({int(player.rect.centerx)}, {int(player.rect.centery)})", True, (255, 255, 255))
        self.display_surface.blit(coord_text, (20, 20))


# ========== Game Init ==========
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

camera_group = CameraGroup()
player = Red_car((9160, 5900), camera_group)

# ========== Game Loop ==========
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()

    camera_group.update()
    camera_group.custom_draw(player)
    pygame.display.update()
    clock.tick(60)
