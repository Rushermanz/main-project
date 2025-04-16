import pygame
import sys
import math

pygame.init()

# Set fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Pixel Racer Prototype")

# Load track and car images
track_img = pygame.image.load("assets/belgium.png").convert()
car_image = pygame.image.load("assets/red_car.png").convert_alpha()
car_image = pygame.transform.scale(car_image, (40, 20))

# Car properties
car_pos = pygame.Vector2(2700, 1200)  # Approx white line starting position
car_angle = 0  # Facing right
speed = 0
max_speed = 3.0
acceleration = 0.07
deceleration = 0.05
turn_speed = 2.5  # degrees/frame

# Lap and timer
lap = 0
lap_started = False
start_time = pygame.time.get_ticks()
finish_time = 0

font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# Camera offset
def get_camera_offset(pos):
    return pygame.Vector2(pos.x - WIDTH // 2, pos.y - HEIGHT // 2)

running = True
while running:
    dt = clock.tick(60)
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        speed = min(speed + acceleration, max_speed)
    elif keys[pygame.K_DOWN]:
        speed = max(speed - acceleration, -max_speed / 2)
    else:
        if speed > 0:
            speed = max(speed - deceleration, 0)
        elif speed < 0:
            speed = min(speed + deceleration, 0)

    if keys[pygame.K_LEFT]:
        car_angle += turn_speed
    if keys[pygame.K_RIGHT]:
        car_angle -= turn_speed

    # Movement
    rad = math.radians(car_angle)
    velocity = pygame.Vector2(math.cos(rad), -math.sin(rad)) * speed
    car_pos += velocity

    # Lap timer
    if 2650 < car_pos.x < 2750 and 1150 < car_pos.y < 1250:
        if not lap_started:
            lap += 1
            finish_time = (pygame.time.get_ticks() - start_time) / 1000
            start_time = pygame.time.get_ticks()
            lap_started = True
    else:
        lap_started = False

    camera_offset = get_camera_offset(car_pos)
    screen.blit(track_img, (-camera_offset.x, -camera_offset.y))

    # Draw car
    rotated_car = pygame.transform.rotate(car_image, car_angle)
    car_rect = rotated_car.get_rect(center=(car_pos.x - camera_offset.x, car_pos.y - camera_offset.y))
    screen.blit(rotated_car, car_rect.topleft)

    # HUD
    time_text = font.render(f"Lap Time: {finish_time:.2f}s", True, (255, 255, 255))
    lap_text = font.render(f"Lap: {lap}", True, (255, 255, 255))
    screen.blit(time_text, (20, 20))
    screen.blit(lap_text, (20, 60))

    pygame.display.flip()

pygame.quit()
sys.exit()
