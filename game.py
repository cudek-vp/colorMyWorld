from __future__ import annotations
from math import inf


from typing import Optional

from arcade import Texture

"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"

OBJECTS_LAYER = "objects"
ENEMIES_LAYER = "enemies"

class Enemy(arcade.Sprite):
    velocity_ratio = 100

    def __init__(self, filename: str = "./resources/enemy.png", scale: float = 0.05, image_x: float = 0, image_y: float = 0,
                 image_width: float = 0, image_height: float = 0, center_x: float = 0, center_y: float = 0,
                 repeat_count_x: int = 1, repeat_count_y: int = 1, flipped_horizontally: bool = False,
                 flipped_vertically: bool = False, flipped_diagonally: bool = False,
                 hit_box_algorithm: Optional[str] = "Simple", hit_box_detail: float = 4.5, texture: Texture = None,
                 angle: float = 0):
        super().__init__(filename, scale, image_x, image_y, image_width, image_height, center_x, center_y,
                         repeat_count_x, repeat_count_y, flipped_horizontally, flipped_vertically, flipped_diagonally,
                         hit_box_algorithm, hit_box_detail, texture, angle)

        self.has_color = False

    def on_update(self, delta_time: float = 1 / 60):
        self.move(delta_time)
    def move(self, delta_time: float = 1 / 60):
        self.center_x += delta_time*self.change_x

    def steal(self, color):
        self.color = color
        self.has_color = True

    def destroy(self):
        self.remove_from_sprite_lists()


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


class Game(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        self.scene = Optional[arcade.Scene]

        self.setup()
        # If you have sprite lists, you should create them here,
        # and set them to None

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        # Create your sprites and sprite lists here
        self.tile_map = arcade.load_tilemap("./resources/kitchen.tmj", 0.2)
        #
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # self.scene = arcade.Scene()
        # self.scene.add_sprite_list(OBJECTS_LAYER, True, arcade.SpriteList())
        sprite = Object("./resources/table.png")
        sprite.center_x = 300
        sprite.center_y = 300
        sprite.color = arcade.color.BROWN

        colors = vars(arcade.color)
        objects = arcade.SpriteList()
        sprites = []
        for sprite in self.scene[OBJECTS_LAYER]:
            o = Object()
            o.texture = sprite.texture
            o.scale = sprite.scale
            o.center_x = sprite.center_x
            o.center_y  =   sprite.center_y
            sprites.append(sprite)
            objects.append(o)
            try:
                o.color = colors[sprite.properties["color"]]
            except KeyError:
                o.color = arcade.color.WHITE

        for sprite in sprites:
            sprite.remove_from_sprite_lists()

        for object in objects:
            self.scene.add_sprite(OBJECTS_LAYER, object)

        self.scene.add_sprite_list(ENEMIES_LAYER, False, arcade.SpriteList())
        enemy = Enemy()
        enemy.center_x = 900
        enemy.center_y = 100
        enemy.change_x = -Enemy.velocity_ratio
        enemy.color = arcade.color.LIGHT_GRAY

        # self.scene.add_sprite(OBJECTS_LAYER, sprite)
        self.scene.add_sprite(ENEMIES_LAYER, enemy)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()
        self.scene.draw()

        # Call draw() on all your sprite lists below

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.scene.on_update(delta_time)

        new_enemies = []

        for enemy in self.scene[ENEMIES_LAYER]:
            if not enemy.has_color:
                objects = arcade.check_for_collision_with_list(enemy, self.scene[OBJECTS_LAYER])
                for object in objects:
                    if object.has_color:
                        enemy.steal(object.color)
                        enemy.change_x = -enemy.change_x
                        object.remove_color()
                        new_enemy = Enemy(center_x=enemy.center_x, center_y=enemy.center_y)
                        new_enemy.change_x = -enemy.change_x
                        new_enemies.append(new_enemy)
                        self.scene.add_sprite(ENEMIES_LAYER, new_enemy)
                        break



    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        pass

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        if not len(self.scene[ENEMIES_LAYER]):
            return
        enemy = self.scene[ENEMIES_LAYER][-1]

        if enemy.has_color:
            closest_sprite = self.get_closest_colored_sprite(enemy)
            if closest_sprite:
                closest_sprite.give_color(enemy.color)

        enemy.destroy()

    def get_closest_colored_sprite(self, sprite) -> Object:
        min = inf
        closest_sprite = None
        for o in self.scene[OBJECTS_LAYER]:
            if not o.has_color:
                distance = arcade.get_distance_between_sprites(sprite, o)
                if distance < min:
                    min = distance
                    closest_sprite = o
        return closest_sprite
    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass


def main():
    """ Main function """
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()