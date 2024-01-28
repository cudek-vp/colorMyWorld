from __future__ import annotations
import time
import arcade
class AnimatedSprite(arcade.Sprite):
    # How many pixels to move before we change the texture in the walking animation
    DEAD_ZONE = 0.1
    RIGHT_FACING = 0
    LEFT_FACING = 1
    def __init__(self, filename: str = './resources/mr carrot.png', scale: float = 0.04, image_x: float = 0, image_y: float = 0,
                 image_width: float = 0, image_height: float = 0, center_x: float = 0, center_y: float = 0,
                 repeat_count_x: int = 1, repeat_count_y: int = 1, flipped_horizontally: bool = False,
                 flipped_vertically: bool = False, flipped_diagonally: bool = False,
                 hit_box_algorithm: Optional[str] = "Simple", hit_box_detail: float = 4.5, texture: Texture = None,
                 angle: float = 0, distance_to_change: int = 20, jump_path = None, walk_path = None, idle_path = None, sprites: int = 8, idle_bool = True):
        super().__init__(filename, scale, image_x, image_y, image_width, image_height, center_x, center_y,
                         repeat_count_x, repeat_count_y, flipped_horizontally, flipped_vertically, flipped_diagonally,
                         hit_box_algorithm, hit_box_detail, texture, angle)

        self.x_moved = 0
        # How far have we traveled horizontally and vertically since changing the texture
        self.x_odometer = 0
        self.y_odometer = 0
        # Hit box will be set based on the first image used.
        self.hit_box = self.texture.hit_box_points
        self.character_face_direction = AnimatedSprite.RIGHT_FACING
        # Index of our current texture
        self.cur_texture = 0
        self.distance_to_change = distance_to_change
        self.walk_path = walk_path
        self.jump_path = jump_path
        self.idle_path = idle_path
        self.sprites = sprites
        self.idle_bool = idle_bool
        self.idle_count = 1
        self.setup()

    def setup(self):

        # self.player_texture_pair = arcade.load_texture_pair(f"{main_path}_player.png")

        self.walk_textures = []
        for i in range(self.sprites):
            texture = arcade.load_texture_pair(f"{self.walk_path}{i}.png")
            self.walk_textures.append(texture)

        self.jump_textures = []
        for i in range(self.sprites):
            texture = arcade.load_texture_pair(f"{self.jump_path}{i}.png")
            self.jump_textures.append(texture)

        self.idle_textures = []
        for i in range(self.sprites):
            texture = arcade.load_texture_pair(f"{self.idle_path}{i}.png")
            self.idle_textures.append(texture)


    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        super().pymunk_moved(physics_engine, dx, dy, d_angle)
        self.x_moved += abs(dx)
        # Figure out if we need to face left or right
        if dx < -AnimatedSprite.DEAD_ZONE and self.character_face_direction == AnimatedSprite.RIGHT_FACING:
            self.character_face_direction = AnimatedSprite.LEFT_FACING
        elif dx > AnimatedSprite.DEAD_ZONE and self.character_face_direction == AnimatedSprite.LEFT_FACING:
            self.character_face_direction = AnimatedSprite.RIGHT_FACING

        # Are we on the ground?
        is_on_ground = physics_engine.is_on_ground(self)

        # Add to the odometer how far we've moved
        self.x_odometer += dx
        self.y_odometer += dy

        # Have we moved far enough to change the texture?
        if abs(self.x_odometer) > self.distance_to_change:

            # Reset the odometer
            self.x_odometer = 0

            # Advance the walking animation
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]

        elif abs(self.y_odometer) > self.distance_to_change:

            # Reset the odometer
            self.y_odometer = 0

            # Advance the jumping animation
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.jump_textures[self.cur_texture][self.character_face_direction]

        else:
            if self.idle_bool and self.idle_count%20 == 0:
                self.idle_count = 1
                self.cur_texture += 1
                if self.cur_texture > 7:
                    self.cur_texture = 0
                self.texture = self.idle_textures[self.cur_texture][self.character_face_direction]
            else:
                self.idle_count += 1
