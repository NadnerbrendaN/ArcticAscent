import random
import pygame
import sys

# Constant Definition
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
FRICTION = 0.15
CAMERA_SMOOTH = 0.1
NUM_SNOWFLAKES = 100

RED = (243, 139, 168)
GREEN = (166, 227, 161)
BLUE = (137, 180, 250)
DARK_BLUE = (0, 35, 130)
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

end_font = pygame.font.SysFont('Rockwell', 60)

max_platform_y = 600
background = pygame.image.load("background.png").convert()
lava = pygame.image.load("lava.png").convert()
death_1 = pygame.image.load("death_1.png").convert()
death_2 = pygame.image.load("death_2.png").convert()

dead = 0
initials = ""

# Camera class for smooth following
class Camera:
    def __init__(self):
        self.y = 0
        self.target_y = 0

    def update(self, player_y):
        self.target_y = player_y - 350
        self.y += (self.target_y - self.y) * CAMERA_SMOOTH

    def apply(self, entity_y):
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

        # Store original position for safer collision resolution
        original_x = self.rect.x
        original_y = self.rect.y

        # Handle horizontal movement
        if x != 0:
            self.rect.x += x
            if self.grounded and x != 0:
                self.vx -= self.vx * FRICTION

            if self.vx > 0:
                self.image = self.image_right
            elif self.vx < 0:
                self.image = self.image_left

            # Screen wrapping
            if self.rect.x + self.rect.width > SCREEN_WIDTH:
                self.rect.x = SCREEN_WIDTH - self.rect.width
            elif self.rect.x < 0:
                self.rect.x = 0

            # Check for horizontal collisions
            collision = pygame.sprite.spritecollideany(self, platforms)
            if collision:
                # Revert to original position and stop horizontal movement
                self.rect.x = original_x
                self.vx = 0

        # Update original_x after horizontal movement is finalized
        original_x = self.rect.x

        # Handle vertical movement separately
        if y != 0:
            self.rect.y += y

            # Check for vertical collisions
            collision = pygame.sprite.spritecollideany(self, platforms)
            if collision:
                if y > 0:  # Moving down (landing on platform)
                    self.rect.bottom = collision.rect.top
                    self.grounded = True
                    self.vy = 0
                    self.collided = collision
                else:  # Moving up (hitting platform from below)
                    self.rect.top = collision.rect.bottom
                    self.vy = 0

        if self.rect.y < self.max_height:
            self.max_height = self.rect.y

    def nudge(self, x, y):
        self.vx += x
        self.vy += y
        if self.vy > 20:
            self.vy = 20

    def ground_check(self):
        global dead

        self.rect.y += 2
        self.collided = pygame.sprite.spritecollideany(self, platforms)

        if isinstance(self.collided, Lava) and dead == 0:
            dead = 1

        self.grounded = self.collided is not None
        self.rect.y -= 2

    def draw(self, camera):
        screen_y = camera.apply(self.rect.y)
        screen.blit(self.image, (self.rect.x, screen_y))


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.image.load('ice_texture.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.world_y = y

    def draw(self, camera):
        screen_y = camera.apply(self.world_y)
        screen.blit(self.image, (self.rect.x, screen_y))

class Lava(Platform):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.image = pygame.image.load('lava.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.world_y = y
        self.orig_y = y

class MovingPlatform(Platform):
    def __init__(self, x, y, w, h, vel):
        super().__init__(x, y, w, h)
        self.velocity = vel

    def tick(self):
        # Move the platform first
        self.rect.x += self.velocity
        if self.rect.x + self.rect.width < 50 or self.rect.x + 50 > SCREEN_WIDTH:
            self.velocity *= -1
            self.rect.x += 2 * self.velocity

        # Move player with platform if standing on it
        if player.grounded and player.collided is self:
            player.rect.x += self.velocity

            # Keep player on screen when riding platform
            if player.rect.x + player.rect.width > SCREEN_WIDTH:
                player.rect.x = SCREEN_WIDTH - player.rect.width
            elif player.rect.x < 0:
                player.rect.x = 0


platforms = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

player = Player(0, 580)
camera = Camera()  # Create camera instance
frames_from_start = 0

# Create snowflakes
snowflakes = [Snowflake() for _ in range(NUM_SNOWFLAKES)]

#lava
for y in range(0, 25):
    lav = Lava(0, SCREEN_HEIGHT + 720 - 20 * y, 500, 20);
    platforms.add(lav)
    all_sprites.add(lav)

# Beginning platform
for x in range(3):
    for y in range(15):
        plat = Platform(200 * x, SCREEN_HEIGHT + y * 20, 640, 300)
        platforms.add(plat)
        all_sprites.add(plat)


target_position = (0, 0)

# Loop
running = True
frames = 0
while running:
    frames += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and dead != 1:
                player = Player(0, 580)
                dead = 0
                frames_from_start = 0
                for platform in platforms:
                    if isinstance(platform, Lava):
                        platform.world_y = platform.orig_y
                        platform.rect.y = platform.orig_y
            if dead == 1 and event.key == pygame.K_RETURN and len(initials) == 3:
                with open("scores.txt", "a") as f:
                    f.write(initials+","+str(585-player.max_height)+"\n")
                dead = 2
            if dead == 1 and event.key == pygame.K_BACKSPACE and len(initials) > 0:
                initials = initials[:-1]
                print(initials)
            if dead == 1 and len(pygame.key.name(event.key)) == 1 and not pygame.key.name(event.key).isnumeric() and len(initials) < 3:
                initials += pygame.key.name(event.key)
                print(initials)
        if event.type == pygame.MOUSEBUTTONUP and player.grounded:
            player.grounded = False
            target_position = pygame.mouse.get_pos()
            player.nudge((target_position[0] - player.rect.centerx) / (SCREEN_WIDTH / 10),
                         (target_position[1] - 350) / (SCREEN_HEIGHT / 30))

    if player.max_height - 400 < max_platform_y:
        # Left platforms
        plat = MovingPlatform(0, max_platform_y - 115, 200, 20, random.randint(1, 4))
        platforms.add(plat)
        all_sprites.add(plat)

        # Right platforms
        plat = MovingPlatform(SCREEN_WIDTH - 200, max_platform_y - 250, 200, 20, random.randint(1, 4))
        platforms.add(plat)
        all_sprites.add(plat)

        max_platform_y -= 250

    # Update moving platforms BEFORE player movement
    for platform in platforms.sprites():
        if isinstance(platform, MovingPlatform):
            platform.tick()
        if isinstance(platform, Lava) and frames_from_start != 0:
            platform.world_y -= ((585-player.max_height - 500)**0.01)/3
            platform.rect.y = platform.world_y

    if not player.grounded:
        player.nudge(0, GRAVITY)

    player.ground_check()

    player.move(None, None)

    if 585 - player.max_height >= 500:
        frames_from_start += 1

    # Update camera to follow player smoothly
    if 0 < frames_from_start <= 180 and player.grounded:
        camera.update(585)
    else:
        camera.update(player.rect.y)

    # Update snowflakes
    for snowflake in snowflakes:
        snowflake.update(camera)

    score = font.render(str(max(0, 585 - player.max_height)), True, BLACK)
    end_score = end_font.render(str(max(0, 585 - player.max_height)), True, DARK_BLUE)

    # Screen drawing
    screen.blit(background, (0, 0))

    # Draw platforms with camera offset
    for platform in platforms.sprites():
        if not isinstance(platform, Lava):
            platform.draw(camera)

    for platform in platforms.sprites():
        if isinstance(platform, Lava):
            platform.draw(camera)

    # Draw player with camera offset
    player.draw(camera)

    screen.blit(score, (SCREEN_WIDTH / 2 - score.get_width() / 2, 30))

    pygame.draw.circle(screen, RED, target_position, 3)

    # Draw snowflakes on top
    for snowflake in snowflakes:
        snowflake.draw(camera)

    # death screen
    if dead == 1:
        screen.blit(death_1, (0, 0))
        screen.blit(end_score, (275, 350))
    elif dead == 2:
        screen.blit(death_2, (0, 0))

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
sys.exit()