import pygame
import sys

# Constant Definition
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60
GRAVITY = 0.5 # The force of gravity
FRICTION = 0.05 # The constant of friction

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ball Jump")
clock = pygame.time.Clock()

# Class Definitions
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('green_circle.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.vx = 0 # Instance fields for velocity
        self.vy = 0
        self.grounded = False # Is the ball on the ground?

    def move(self, x, y): # Move the player
        if x is None: # If we don't give numbers -- just to apply the stored velocity
            x = self.vx
        if y is None:
            y = self.vy
        self.rect.x += x # Move in the x direction
        if self.grounded and x != 0: # If we're on the ground and rolling
            self.vx -= self.vx * FRICTION # Slow down with friction
        while pygame.sprite.spritecollideany(self, platforms):
            self.rect.x -= x / abs(x)
        self.rect.y += y
        while pygame.sprite.spritecollideany(self, platforms):
            self.rect.y -= y / abs(y)
            self.grounded = True
            self.vy = 0

    def nudge(self, x, y):
        self.vx += x
        self.vy += y

    def ground_check(self):
        self.rect.y += 1
        if pygame.sprite.spritecollideany(self, platforms):
            self.grounded = True
        self.rect.y -= 1

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.surface.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))

player_group = pygame.sprite.Group()
platforms = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

player = Player(0, 0)
player_group.add(player)

platforms.add(Platform(0, 420, 640, 60))
platforms.add(Platform(100, 400, 100, 20))

all_sprites.add(player_group, platforms)

target_position = (-10, -10)

# Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP and player.grounded:
            player.grounded = False
            target_position = pygame.mouse.get_pos()
            player.nudge((target_position[0] - player.rect.centerx) / (SCREEN_WIDTH/10),
            (target_position[1] - player.rect.centery) / (SCREEN_HEIGHT/20))

    if not player.grounded:
        player.nudge(0, GRAVITY)
    else:
        player.ground_check()

    player.move(None, None)

    # Screen drawing
    screen.fill(BLUE)
    all_sprites.draw(screen)
    pygame.draw.circle(screen, RED, target_position, 1)

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
sys.exit()