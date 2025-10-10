import random

import pygame
import sys

# Constant Definition
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
FRICTION = 0.05
CAMERA_SMOOTH = 0.2  # Camera smoothing factor (0.1 = smooth, 1.0 = instant)
NUM_SNOWFLAKES = 100  # Number of snowflakes

RED = (243, 139, 168)
GREEN = (166, 227, 161)
BLUE = (137, 180, 250)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ball Jump")
clock = pygame.time.Clock()

pygame.font.init()
font = pygame.font.SysFont('Rockwell', 30)
score = font.render(str(0), True, RED)

max_platform_y = -880
background = pygame.image.load("background.png").convert()

max_platform_y = 600


# Camera class for smooth following
class Camera:
    def __init__(self):
        self.y = 0  # Current camera y position
        self.target_y = 0  # Where the camera wants to be

    def update(self, player_y):
        # The target is to keep the player at a certain position on screen (e.g., y=350)
        self.target_y = player_y - 350

        # Smoothly interpolate towards the target
        self.y += (self.target_y - self.y) * CAMERA_SMOOTH

    def apply(self, entity_y):
        # Convert world position to screen position
        return entity_y - self.y


# Snowflake class for atmospheric effect
class Snowflake:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-SCREEN_HEIGHT, SCREEN_HEIGHT)
        self.speed = random.uniform(1, 3)
        self.drift = random.uniform(-0.5, 0.5)
        self.size = random.randint(1, 3)

    def update(self, camera):
        self.y += self.speed
        self.x += self.drift

        # Wrap around screen
        if self.y > SCREEN_HEIGHT:
            self.y = camera.y - SCREEN_HEIGHT
            self.x = random.randint(0, SCREEN_WIDTH)
        if self.x > SCREEN_WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = SCREEN_WIDTH

    def draw(self, camera):
        screen_y = camera.apply(self.y)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(screen_y)), self.size)


# Class Definitions
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image_right = pygame.image.load('penguin_right.png').convert_alpha()
        self.image_left = pygame.transform.flip(self.image_right, True, False)

        self.image = self.image_right
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        self.collided = None
        self.max_height = y

        self.vx = 0
        self.vy = 0
        self.grounded = False

    def move(self, x, y):
        if x is None:
            x = self.vx
        if y is None:
            y = self.vy

        if x != 0:
            self.rect.x += x
            if self.grounded and x != 0:
                self.vx -= self.vx * FRICTION

            if self.vx > 0:
                self.image = self.image_right
            elif self.vx < 0:
                self.image = self.image_left

            if self.rect.x + self.rect.width > SCREEN_WIDTH:
                self.rect.x = SCREEN_WIDTH - self.rect.width
            elif self.rect.x < 0:
                self.rect.x = 0
            while pygame.sprite.spritecollideany(self, platforms):
                self.rect.x -= x / abs(x)
                self.vx = 0

        self.rect.y += y
        while pygame.sprite.spritecollideany(self, platforms):
            self.rect.y -= y / abs(y)
            self.grounded = True
            self.vy = 0

        if self.rect.y < self.max_height:
            self.max_height = self.rect.y

    def nudge(self, x, y):
        self.vx += x
        self.vy += y
        if self.vy < -20:
            self.vy = -20

    def ground_check(self): # See if we're grounded
        self.rect.y += 1 # Try moving down
        self.collided = pygame.sprite.spritecollideany(self, platforms)
        self.grounded = self.collided is not None
        self.rect.y -= 1 # Move back up

    def draw(self, camera):
        # Use camera to determine screen position
        screen_y = camera.apply(self.rect.y)
        screen.blit(self.image, (self.rect.x, screen_y))

player = Player(0, 450)
player_group = pygame.sprite.Group()
player_group.add(player)

class Platform(pygame.sprite.Sprite): # Platforms
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.image.load('ice_texture.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.world_y = y  # Store the world position

    def draw(self, camera):
        # Use camera to determine screen position
        screen_y = camera.apply(self.world_y)
        screen.blit(self.image, (self.rect.x, screen_y))


class MovingPlatform(Platform):
    def __init__(self, x, y, w, h, vel):
        super().__init__(x, y, w, h)
        self.velocity = vel

    def tick(self):
        self.rect.x += self.velocity
        if self.rect.x + self.rect.width < 0 or self.rect.x > SCREEN_WIDTH:
            self.velocity *= -1
            self.rect.x += 2*self.velocity
        if player.grounded and player.collided is self:
            player.rect.x += self.velocity

platforms = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

player = Player(0, 450)
camera = Camera()  # Create camera instance

# Create snowflakes
snowflakes = [Snowflake() for _ in range(NUM_SNOWFLAKES)]

for x in range(3):
    for y in range(15):
        plat = Platform(200 * x, SCREEN_HEIGHT + y * 20, 640, 300)
        platforms.add(plat)
        all_sprites.add(plat)

    platforms.add(MovingPlatform(w - 200, y * 250 - (900), w, 20, random.randint(1, 4)))

for y in range(8): # right side platforms
    #x = random.randint(0,SCREEN_WIDTH - 100)
    w = random.randint(100, 180)

    platforms.add(MovingPlatform(SCREEN_WIDTH - w, y * 250 - (900 + 115), w, 20, random.randint(1, 4)))

all_sprites.add(platforms)

target_position = (0, 0) # Set the player's click offscreen temporarily

# Loop
running = True
frames = 0
while running:
    frames += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP and player.grounded:
            player.grounded = False
            target_position = pygame.mouse.get_pos()
            player.nudge((target_position[0] - player.rect.centerx) / (SCREEN_WIDTH / 10),
                         (target_position[1] - 350) / (SCREEN_HEIGHT / 30))

    if player.max_height - 400 < max_platform_y:
        # Left platforms
        w = random.randint(75, 200)
        plat = MovingPlatform(0, max_platform_y - 80, w, 20, random.randint(1, 4))
        platforms.add(plat)
        all_sprites.add(plat)

        # Right platforms
        w = random.randint(75, 200)
        plat = MovingPlatform(SCREEN_WIDTH - w, max_platform_y - 200, w, 20, random.randint(1, 4))
        platforms.add(plat)
        all_sprites.add(plat)

        max_platform_y -= 250

    if not player.grounded:
        player.nudge(0, GRAVITY)
    else:
        player.ground_check()

    player.move(None, None)

    # Update camera to follow player smoothly
    camera.update(player.rect.y)

    # Update snowflakes
    for snowflake in snowflakes:
        snowflake.update(camera)

    score = font.render(str(585 - player.rect.y), True, BLACK)

    # Screen drawing
    screen.blit(background, (0, 0))

    # Draw platforms with camera offset
    for platform in platforms.sprites():
        platform.draw(camera)

    # Draw player with camera offset
    player.draw(camera)

    pygame.draw.circle(screen, RED, target_position, 3)

    # Draw snowflakes on top (separate from camera, stays on screen)
    for snowflake in snowflakes:
        snowflake.draw(camera)

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
sys.exit()