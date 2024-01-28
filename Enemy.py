from typing import Optional
import random
import arcade
from arcade import Texture
from AnimatedSprite import AnimatedSprite
class Enemy(AnimatedSprite):
    velocity_ratio = 100
    sprites_number = 0

    def __init__(self, filename: str = './resources/egg 0.png', scale: float = 0.04, image_x: float = 0,
                 image_y: float = 0, image_width: float = 0, image_height: float = 0, center_x: float = 0,
                 center_y: float = 0, repeat_count_x: int = 1, repeat_count_y: int = 1,
                 flipped_horizontally: bool = False, flipped_vertically: bool = False, flipped_diagonally: bool = False,
                 hit_box_algorithm: Optional[str] = "Simple", hit_box_detail: float = 4.5, texture: Texture = None,
                 angle: float = 0, distance_to_change: int = 50, jump_path='./resources/egg jump ', walk_path='./resources/egg ', idle_path='./resources/egg idle ',
                 sprites: int = 8, idle_bool=False):
        super().__init__(filename, scale, image_x, image_y, image_width, image_height, center_x, center_y,
                         repeat_count_x, repeat_count_y, flipped_horizontally, flipped_vertically, flipped_diagonally,
                         hit_box_algorithm, hit_box_detail, texture, angle, distance_to_change, jump_path, walk_path,
                         idle_path, sprites, idle_bool)

        self.has_color = False
        self.move_time = 1
        self.time = self.move_time
        self.move_force = 0
        Enemy.sprites_number += 1

    def steal(self, color):
        self.color = color
        self.has_color = True

    def split(self):
        n = random.sample([1, 2], counts=[3, 1], k=1)[0]
        return [Enemy(center_x=self.center_x, center_y=self.center_y) for i in range(0)]


    def on_update(self, delta_time: float = 1 / 60):
        super().on_update()
        if self.center_y < -10:
            self.destroy()


    def destroy(self):
        self.remove_from_sprite_lists()
        Enemy.sprites_number -= 1