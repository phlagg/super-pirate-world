from settings import *
from sprites import Sprite, Cloud
from random import choice, randint
from timer import Timer

class WorldSprites(pygame.sprite.Group):
    def __init__(self, data):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.data = data
        self.offset = vector()

    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)
        # background
        for sprite in sorted(self, key = lambda sprite: sprite.z):
            if sprite.z < Z_LAYERS['main']:
                if sprite.z == Z_LAYERS['path']:
                    if sprite.level <= self.data.unlocked_level:
                        self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
                else:
                    self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
        # main
        for sprite in sorted(self, key = lambda sprite: sprite.rect.centery):
            if sprite.z ==Z_LAYERS['main']:
                if hasattr(sprite, 'icon'):
                    self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset + vector(0,-20))
                else:
                    self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)

class AllSprites(pygame.sprite.Group):
    def __init__(self, width, height, clouds, horizon_line, bg_tile = None, top_limit = 0) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector(0, 0)
        self.width, self.height = width * TILE_SIZE, height * TILE_SIZE
        self.borders = {
            'left': 0,
            'right': -self.width + WINDOW_WIDTH,
            'bottom': -self.height + WINDOW_HEIGHT, 
            'top': top_limit
        }
        self.sky = not bg_tile
        self.horizon_line = horizon_line

        if bg_tile:
            for col in range(width):
                for row in range(-int(top_limit/TILE_SIZE)-1, height):
                    x,y = col*TILE_SIZE, row *TILE_SIZE
                    Sprite(
                        pos= (x,y),
                        surf= bg_tile,
                        groups= self,
                        z= -1)
        else: # sky
            self.large_cloud = clouds['large']
            self.small_clouds = clouds ['small']
            self.cloud_direction = -1

            # large cloud
            self.large_cloud_speed = 50
            self.large_cloud_x = 0
            self.large_cloud_tiles = int(self.width / self.large_cloud.get_width()) + 2
            self.large_cloud_width, self.large_cloud_height = self.large_cloud.get_size()
            
            # small clouds
            self.small_cloud_speed = 50
            self.create_small_clouds(20)
            # timer -> cloud every 2.5 s
            self.cloud_timer = Timer(2500, self.create_small_clouds, True)
            self.cloud_timer.activate()
            # lots of clouds by default
                    
    def camera_constraint(self):
        self.offset.x = self.offset.x if self.offset.x < self.borders['left'] else self.borders['left']
        self.offset.x = self.offset.x if self.offset.x > self.borders['right'] else self.borders['right']
        self.offset.y = self.offset.y if self.offset.y < self.borders['top'] else self.borders['top']
        self.offset.y = self.offset.y if self.offset.y > self.borders['bottom'] else self.borders['bottom']

    def create_small_clouds(self, num_clouds = 1):
        for cloud in range(num_clouds):
            cloud_start_x = randint(self.width+500, self.width+700) if num_clouds == 1 \
                        else randint(0, self.width)
            Cloud(
                pos= ( cloud_start_x, randint(self.borders['top'], self.horizon_line)),
                surf= choice(self.small_clouds),
                groups=self,
                speed= randint(50,120),
                direction= self.cloud_direction)

    def draw_large_cloud(self, dt):
        self.large_cloud_x += self.large_cloud_speed * self.cloud_direction * dt
        if self.large_cloud_x <= -self.large_cloud_width:
            self.large_cloud_x = 0
        for cloud in range(self.large_cloud_tiles):
            left = self.large_cloud_x + self.large_cloud_width * cloud + self.offset.x
            top = self.horizon_line - self.large_cloud_height + self.offset.y
            self.display_surface.blit(self.large_cloud, (left, top))

    def draw_sky(self):
        self.display_surface.fill('#ddc6a1')
        horizon_pos = self.horizon_line + self.offset.y
        sea_rect = pygame.FRect(0,horizon_pos, WINDOW_WIDTH, WINDOW_HEIGHT - horizon_pos)
        pygame.draw.rect(self.display_surface, '#92a9ce', sea_rect)
        # horizon line
        pygame.draw.line(self.display_surface,'#f5f1de', (0,horizon_pos), (WINDOW_WIDTH, horizon_pos), 4)

    def draw(self, target_pos, dt):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)
        self.camera_constraint()
        if self.sky:
            self.cloud_timer.update()   
            self.draw_sky()
            self.draw_large_cloud(dt)
        for sprite in sorted(self, key=lambda sprite: sprite.z):
            offset_pos = sprite.rect.topleft + self.offset
            self.display_surface.blit(sprite.image, offset_pos)

