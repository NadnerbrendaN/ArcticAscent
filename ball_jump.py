import random

import pygame
import sys

# Constant Definition
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5 # The force of gravity
FRICTION = 0.05 # The constant of friction

RED = (243, 139, 168)
GREEN = (166, 227, 161)
BLUE = (137, 180, 250)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ball Jump")
clock = pygame.time.Clock()

# Class Definitions
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('mauve_ball.png').convert_alpha()
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

        if x != 0:
            self.rect.x += x # Move in the x direction
            if self.grounded and x != 0: # If we're on the ground and rolling
                self.vx -= self.vx * FRICTION # Slow down with friction
            if self.rect.x + self.rect.width > SCREEN_WIDTH: # If the player is offscreen to the right
                self.rect.x = SCREEN_WIDTH - self.rect.width # Stay just on screen on the right
            elif self.rect.x < 0: # If the player is offscreen to the left
                self.rect.x = 0 # Stay just on screen on the right
            while pygame.sprite.spritecollideany(self, platforms): # If in an obstacle
                self.rect.x -= x / abs(x) # Move out by one pixel

        self.rect.y += y # Move in the y direction
        while pygame.sprite.spritecollideany(self, platforms): # If in an obstacle
            self.rect.y -= y / abs(y) # Move out by one pixel
            self.grounded = True # We are on the ground
            self.vy = 0 # Stop falling (set y velocity to 0)

    def nudge(self, x, y): # Add velocity
        self.vx += x # Add to x velocity
        self.vy += y # Add to y velocity

    def ground_check(self): # See if we're grounded
        self.rect.y += 1 # Try moving down
        self.grounded = pygame.sprite.spritecollideany(self, platforms)
        self.rect.y -= 1 # Move back up

class Platform(pygame.sprite.Sprite): # Platforms
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.surface.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))

    def scroll(self, y):
        self.rect.y += y

player_group = pygame.sprite.Group()
platforms = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

player = Player(0, 450)
player_group.add(player)

platforms.add(Platform(0, SCREEN_HEIGHT - 60, 640, 60)) # Manually add platforms temporarily before making level setup
#platforms.add(Platform(100, 400, 100, 20))

for y in range(SCREEN_HEIGHT // 3): # left side platforms
    #x = random.randint(0,SCREEN_WIDTH - 100)
    w = random.randint(50, 120)

    platforms.add(Platform(0, y * 160 + 100, w, 20))

for y in range(SCREEN_HEIGHT // 3): # right side platforms
    #x = random.randint(0,SCREEN_WIDTH - 100)
    w = random.randint(50, 120)

    platforms.add(Platform(SCREEN_WIDTH - w, y * 160 + 180, w, 20))

for y in range(SCREEN_HEIGHT // 3):
    add = random.randint(0, 100) < 50

    if(add):
        platforms.add(Platform(SCREEN_WIDTH / 2 - w / 2, y * 160 + 60, 40, 20))

all_sprites.add(player_group, platforms)

target_position = (0, 0) # Set the player's click offscreen temporarily

# Loop
running = True
frames = 0
while running:
    frames += 1
    for event in pygame.event.get(): # All mouse and keyboard events
        if event.type == pygame.QUIT: # Exit game
            running = False
        if event.type == pygame.MOUSEBUTTONUP and player.grounded: # Clicked while on the ground
            player.grounded = False # No longer on the ground
            target_position = pygame.mouse.get_pos() # Target the click
            player.nudge((target_position[0] - player.rect.centerx) / (SCREEN_WIDTH/10),
            (target_position[1] - player.rect.centery) / (SCREEN_HEIGHT/20)) # Math to scale how hard we jump and get the right direction

    if not player.grounded: # If jumping
        player.nudge(0, GRAVITY) # Be affected by gravity
    else: # If on the ground
        player.ground_check() # Check if we're actually on the ground

    player.move(None, None) # Apply player velocity

    for platform in platforms.sprites(): # Loop through all platforms
        if platform.rect.y - player.rect.height > SCREEN_HEIGHT: # If it's below the screen
            platforms.remove(platform) # Kill it
        if frames > 180 and frames % 2: # 30x a second after the first three seconds
            platform.scroll(1) # Move each platform down by one pixel (simulating the screen moving up)
    player.move(0, 1) # Move the player down with them (it's also staying still while the screen moves up)

    # Screen drawing
    screen.fill(BLUE) # Background
    all_sprites.draw(screen) # Draw everything
    pygame.draw.circle(screen, RED, target_position, 3) # Draw a circle where you clicked

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
sys.exit()