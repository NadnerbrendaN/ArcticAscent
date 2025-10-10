import random
import pygame
import sys

# Constant Definition
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5 # The force of gravity
FRICTION = 0.05 # The constant of friction

RED = (243, 139, 168)
GREEN = (166, 227, 161)
BLUE = (137, 180, 250)
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

# Class Definitions
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image_right = pygame.image.load('penguin_right.png').convert_alpha()
        self.image_left = pygame.transform.flip(self.image_right, True, False)

        self.image = self.image_right  # Start facing right
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        self.collided = None
        self.max_height = y

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

            if self.vx > 0: #penguin faces right if vx > 0
                self.image = self.image_right
            elif self.vx < 0: #switch penguin to face left
                self.image = self.image_left

            if self.rect.x + self.rect.width > SCREEN_WIDTH: # If the player is offscreen to the right
                self.rect.x = SCREEN_WIDTH - self.rect.width # Stay just on screen on the right
            elif self.rect.x < 0: # If the player is offscreen to the left
                self.rect.x = 0 # Stay just on screen on the right
            while pygame.sprite.spritecollideany(self, platforms): # If in an obstacle
                self.rect.x -= x / abs(x) # Move out by one pixel
                self.vx = 0 # Ensure that when you hit a wall you don't keep going

        self.rect.y += y # Move in the y direction
        while pygame.sprite.spritecollideany(self, platforms): # If in an obstacle
            self.rect.y -= y / abs(y) # Move out by one pixel
            self.grounded = True # We are on the ground
            self.vy = 0 # Stop falling (set y velocity to 0)

        if self.rect.y < self.max_height:
            self.max_height = self.rect.y

    def nudge(self, x, y): # Add velocity
        self.vx += x # Add to x velocity
        self.vy += y # Add to y velocity
        if self.vy < -20:
            self.vy = -20

    def ground_check(self): # See if we're grounded
        self.rect.y += 1 # Try moving down
        self.collided = pygame.sprite.spritecollideany(self, platforms)
        self.grounded = self.collided is not None
        self.rect.y -= 1 # Move back up

    def draw(self):
        rect = pygame.Rect(self.rect.x, 350, self.rect.width, self.rect.height)
        screen.blit(self.image, rect)

player = Player(0, 450)
player_group = pygame.sprite.Group()
player_group.add(player)

class Platform(pygame.sprite.Sprite): # Platforms
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.image.load('ice_texture.png').convert_alpha()

        # self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))

    def move(self, y):
        self.rect.y += y

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

for x in range(3): #starting platform
    for y in range(15):
        platforms.add(Platform(200 * x, SCREEN_HEIGHT + y * 20, 640, 300))

for y in range(7): # left side platforms
    #x = random.randint(0,SCREEN_WIDTH - 100)
    w = random.randint(100, 180)

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
    for event in pygame.event.get(): # All mouse and keyboard events
        if event.type == pygame.QUIT: # Exit game
            running = False
        if event.type == pygame.MOUSEBUTTONUP and player.grounded: # Clicked while on the ground
            player.grounded = False # No longer on the ground
            target_position = pygame.mouse.get_pos() # Target the click
            player.nudge((target_position[0] - player.rect.centerx) / (SCREEN_WIDTH/10),
            (target_position[1] - 350) / (SCREEN_HEIGHT/30)) # Math to scale how hard we jump and get the right direction

    if player.max_height - 400 < max_platform_y:
        w = random.randint(75, 200)
        plat = MovingPlatform(0, max_platform_y - 80, w, 20, random.randint(1, 4))
        platforms.add(plat)
        all_sprites.add(plat)

        w = random.randint(75, 200)
        plat = MovingPlatform(SCREEN_WIDTH - w, max_platform_y - 200, w, 20, random.randint(1, 4))
        platforms.add(plat)
        all_sprites.add(plat)

        max_platform_y -= 200

    if not player.grounded: # If jumping
        player.nudge(0, GRAVITY) # Be affected by gravity
    else: # If on the ground
        player.ground_check() # Check if we're actually on the ground

    player.move(None, None) # Apply player velocity

    score = font.render(str(585 - player.rect.y), True, BLACK)

    # Screen drawing
    screen.fill(BLUE) # Background
    player.draw()
    for platform in platforms.sprites():
        platform.move(350 + -player.rect.y)
        if isinstance(platform, MovingPlatform):
            platform.tick()
    all_sprites.draw(screen) # Draw everything
    for platform in platforms.sprites():
        platform.move(-350 + player.rect.y)
    pygame.draw.circle(screen, RED, target_position, 3) # Draw a circle where you clicked
    screen.blit(score, (250 - .5*score.get_rect().width, 10))

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
sys.exit()