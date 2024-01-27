from typing import Optional

import arcade
from arcade import Texture

class Enemy(arcade.Sprite):
    velocity_ratio = 100

    def __init__(self, filename: str = "./resources/enemy.png", scale: float = 0.03, image_x: float = 0, image_y: float = 0,
                 image_width: float = 0, image_height: float = 0, center_x: float = 0, center_y: float = 0,
                 repeat_count_x: int = 1, repeat_count_y: int = 1, flipped_horizontally: bool = False,
                 flipped_vertically: bool = False, flipped_diagonally: bool = False,
                 hit_box_algorithm: Optional[str] = "Simple", hit_box_detail: float = 4.5, texture: Texture = None,
                 angle: float = 0):
        super().__init__(filename, scale, image_x, image_y, image_width, image_height, center_x, center_y,
                         repeat_count_x, repeat_count_y, flipped_horizontally, flipped_vertically, flipped_diagonally,
                         hit_box_algorithm, hit_box_detail, texture, angle)
        self.has_color = False
        self.move_time = 0
        self.time = 0
        self.move_force = 0

    def steal(self, color):
        self.color = color
        self.has_color = True

    def split(self):
        return  [Enemy(center_x=self.center_x, center_y=self.center_y) for i in range(1)]


    def on_update(self, delta_time: float = 1 / 60):
        super().on_update()


    def destroy(self):
        self.remove_from_sprite_lists()