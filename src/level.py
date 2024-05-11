from settings import *
from sprites import Sprite, MovingSprite, AnimatedSprite
from player import Player
from groups import AllSprites
from random import uniform

class Level:
    def __init__(self, tmx_map, level_frames):
        self.display_surface = pygame.display.get_surface()
        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.semi_collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        
        self.setup(tmx_map, level_frames)

    def setup(self, tmx_map, level_frames):
        # tiles
        for layer in ['BG', 'Terrain', 'FG', 'Platforms']:  
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer =='Terrain': groups.append(self.collision_sprites)
                if layer == 'Platforms': groups.append(self.semi_collision_sprites)
                match layer:
                    case 'BG': z = Z_LAYERS['bg tiles']
                    case 'FG': z = Z_LAYERS['fg']
                    case   _ : z = Z_LAYERS['main']
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups, z)
            
        # bg details
        for obj in tmx_map.get_layer_by_name("BG details"):
            if 'static' in obj.name:
                Sprite(
                    pos = (obj.x, obj.y), 
                    surf= obj.image, 
                    groups= self.all_sprites,
                    z = Z_LAYERS['bg tiles'] )
            else:            
                AnimatedSprite(
                    pos = (obj.x, obj.y),
                    frames = level_frames[obj.name], 
                    groups = self.all_sprites, 
                    z = Z_LAYERS['bg tiles'], 
                    animation_speed= ANIMATION_SPEED)
                
                if obj.name =='candle':
                    AnimatedSprite(
                        pos = (obj.x, obj.y) + vector(-20,-20),
                        frames = level_frames['candle_light'], 
                        groups = self.all_sprites, 
                        z = Z_LAYERS['bg tiles'], 
                        animation_speed= ANIMATION_SPEED)
                    
            
            # moving objects
            for obj in tmx_map.get_layer_by_name('Moving Objects'):
                if obj.name == 'helicopter':
                    if obj.width > obj.height: # horizontal
                        move_dir  = 'x'
                        start_pos = (obj.x, obj.y + obj.height/2)
                        end_pos   = (obj.x + obj.width, obj.y + obj.height/2)
                    else: # vertical
                        move_dir  = 'y'
                        start_pos = (obj.x + obj.width/2, obj.y)
                        end_pos   = (obj.x + obj.width/2, obj.y + obj.height)
                    speed = obj.properties['speed']
                    MovingSprite([self.all_sprites, self.semi_collision_sprites],start_pos, end_pos, move_dir, speed)
        
        # objects
        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "player":
                self.player = Player(
                    pos = (obj.x, obj.y), 
                    groups = self.all_sprites, 
                    collision_sprites = self.collision_sprites, 
                    semi_collision_sprites = self.semi_collision_sprites,
                    frames = level_frames['player'])
            else:
                # static
                if obj.name in ('barrel', 'crate'):
                    Sprite((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])
                else:
                    # frames
                    frames = level_frames[obj.name] if not 'palm' in obj.name else level_frames['palms'][obj.name]
                    if obj.name == 'floor_spike' and obj.properties['inverted']:
                        frames = [pygame.transform.flip(frame, False, True) for frame in frames]

                    # groups 
                    groups = [self.all_sprites]
                    if obj.name in('palm_small', 'palm_large'): groups.append(self.semi_collision_sprites)
                    if obj.name in ('saw', 'floor_spike'): groups.append(self.damage_sprites)

                    # z index
                    z = Z_LAYERS['main'] if not 'bg' in obj.name else Z_LAYERS['bg details']
                    # animation speed
                    animation_speed = ANIMATION_SPEED if not 'palm' in obj.name else ANIMATION_SPEED + uniform(-1,1)
                    AnimatedSprite((obj.x, obj.y),frames, groups, z, animation_speed)
                


    def run(self, dt):
        self.display_surface.fill("black")
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.player.hitbox_rect.center)