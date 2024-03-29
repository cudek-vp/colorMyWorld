"""
Platformer Game
"""
from __future__ import annotations
from AnimatedSprite import AnimatedSprite
import arcade

class Player(AnimatedSprite):

    def __init__(self, filename: str = './resources/mr carrot.png', scale: float = 0.06, image_x: float = 0,
                 image_y: float = 0, image_width: float = 0, image_height = 0, center_x: float = 0,
                 center_y: float = 0, repeat_count_x: int = 1, repeat_count_y: int = 1,
                 flipped_horizontally: bool = False, flipped_vertically: bool = False, flipped_diagonally: bool = False,
                 hit_box_algorithm: Optional[str] = "Simple", hit_box_detail: float = 4.5, texture: Texture = None,
                 angle: float = 0, distance_to_change: int = 50, jump_path='./resources/mr carrot jump ', walk_path='./resources/mr carrot ', idle_path='./resources/mr carrot idle ',
                 sprites: int = 8, idle_bool=False):
        super().__init__(filename, scale, image_x, image_y, image_width, image_height, center_x, center_y,
                         repeat_count_x, repeat_count_y, flipped_horizontally, flipped_vertically, flipped_diagonally,
                         hit_box_algorithm, hit_box_detail, texture, angle, distance_to_change, jump_path, walk_path,
                         idle_path, sprites, idle_bool)
        self.color = arcade.color.BITTER_LEMON