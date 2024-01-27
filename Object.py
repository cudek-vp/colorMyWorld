import arcade
from typing import Optional
from arcade import Texture
class Object(arcade.Sprite):
    def __init__(self, filename: str = None, scale: float = 0.2, image_x: float = 0, image_y: float = 0,
                 image_width: float = 0, image_height: float = 0, center_x: float = 0, center_y: float = 0,
                 repeat_count_x: int = 1, repeat_count_y: int = 1, flipped_horizontally: bool = False,
                 flipped_vertically: bool = False, flipped_diagonally: bool = False,
                 hit_box_algorithm: Optional[str] = "Simple", hit_box_detail: float = 4.5, texture: Texture = None,
                 angle: float = 0):
        super().__init__(filename, scale, image_x, image_y, image_width, image_height, center_x, center_y,
                         repeat_count_x, repeat_count_y, flipped_horizontally, flipped_vertically, flipped_diagonally,
                         hit_box_algorithm, hit_box_detail, texture, angle)

        self.has_color = True

    def remove_color(self):
        self.color = arcade.color.LIGHT_GRAY
        self.has_color = False

    def give_color(self, color):
        self.color = color
        self.has_color = True