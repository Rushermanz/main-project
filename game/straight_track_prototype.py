import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Racer Prototype")

WHITE = (255, 255, 255)
GRAY = (30, 30, 30)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

car_width, car_height = 40, 20
car_x = 100
car_y = HEIGHT // 2 - car_height // 2
car_color = GREEN

finish_line_x = WIDTH - 100

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
start_time = pygame.time.get_ticks()
finished = False
finish_time = 0

running = True
while running:
    window.fill(GRAY)

    pygame.draw.rect(window, RED, (finish_line_x, 0, 10, HEIGHT))
    pygame.draw.rect(window, car_color, (car_x, car_y, car_width, car_height))

    if not finished:
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
    else:
        elapsed_time = finish_time
    timer_text = font.render(f"Time: {elapsed_time:.2f}s", True, WHITE)
    window.blit(timer_text, (10, 10))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        car_x += 5

    if car_x + car_width >= finish_line_x and not finished:
        finish_time = (pygame.time.get_ticks() - start_time) / 1000
        finished = True

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
