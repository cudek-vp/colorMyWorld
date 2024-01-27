from __future__ import annotations

import random
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
from Object import Object

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"

OBJECTS_LAYER = "objects0"
ENEMIES_LAYER = "enemies"
PLATFORMS_LAYER = "platforms"
WALLS_LAYER = "walls"

# Gravity
GRAVITY = 1500

# Damping - Amount of speed lost per second
DEFAULT_DAMPING = 1.0
PLAYER_DAMPING = 0.4

# Friction between objects
PLAYER_FRICTION = 1.0
WALL_FRICTION = 0.7
DYNAMIC_ITEM_FRICTION = 0.6

# Mass (defaults to 1)
PLAYER_MASS = 2.5

# Keep player from going too fast
PLAYER_MAX_HORIZONTAL_SPEED = 450
PLAYER_MAX_VERTICAL_SPEED = 1600

class Enemy(arcade.Sprite):
    velocity_ratio = 100

    def __init__(self, filename: str = "./resources/enemy.png", scale: float = 0.03, image_x: float = 0, image_y: float = 0,
                 image_width: float = 0, image_height: float = 0, center_x: float = 0, center_y: float = 0,
                 repeat_count_x: int = 1, repeat_count_y: int = 1, flipped_horizontally: bool = False,
                 flipped_vertically: bool = False, flipped_diagonally: bool = False,
                 hit_box_algorithm: Optional[str] = "Simple", hit_box_detail: float = 4.5, texture: Texture = None,
                 angle: float = 0, game : Game = None):
        super().__init__(filename, scale, image_x, image_y, image_width, image_height, center_x, center_y,
                         repeat_count_x, repeat_count_y, flipped_horizontally, flipped_vertically, flipped_diagonally,
                         hit_box_algorithm, hit_box_detail, texture, angle)
        self.has_color = False
        self.game = game
        self.move_time = 0
        self.time = 0

    def steal(self, color):
        self.color = color
        self.has_color = True

    def split(self):
        for i in range(1):
            new_enemy = Enemy(center_x=self.center_x, center_y=self.center_y, game=self.game)
            self.game.scene.add_sprite(ENEMIES_LAYER, new_enemy)
            self.game.physics_engine.add_sprite(new_enemy, friction=PLAYER_FRICTION,
                                           mass=PLAYER_MASS,
                                           collision_type="enemy")

    def on_update(self, delta_time: float = 1 / 60):
        super().on_update()
        self.game.physics_engine.apply_force(self, force=(-100, 0))
        self.game.physics_engine.set_friction(self, 0)

    def destroy(self):
        self.remove_from_sprite_lists()


class Game(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        self.scene : Optional[arcade.Scene]

        self.physics_engine : Optional[arcade.PymunkPhysicsEngine]

        self.setup()
        # If you have sprite lists, you should create them here,
        # and set them to None




    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        # Create your sprites and sprite lists here
        layer_options = {
            WALLS_LAYER: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "Simple"
            }
        }


        self.tile_map = arcade.load_tilemap("./resources/walls.tmj", 0.2, layer_options)
        #
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.physics_engine = arcade.PymunkPhysicsEngine(damping=DEFAULT_DAMPING,
                                                         gravity=(0, -GRAVITY))

        colors = vars(arcade.color)
        objects = arcade.SpriteList()
        sprites = []
        for sprite in self.scene[OBJECTS_LAYER]:
            o = Object()
            o.texture = sprite.texture
            o.scale = sprite.scale
            o.center_x = sprite.center_x
            o.center_y = sprite.center_y
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
        enemy = Enemy( game=self)
        enemy.center_x = 450
        enemy.center_y = 400
        enemy.change_x = -Enemy.velocity_ratio
        enemy.color = arcade.color.LIGHT_GRAY

        def enemy_platform_jump_collide(enemy, _platform, _arbiter, _space, _data):
            po : arcade.PymunkPhysicsObject = self.physics_engine.get_physics_object(enemy)
            return po.body.velocity[1] < 0

        def enemy_enemy_collide(_enemy1, _enemy2, _arbiter, _space, _data):
            return False

        self.physics_engine.add_sprite_list(self.scene[WALLS_LAYER],
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)
        # self.physics_engine.add_sprite_list(self.scene[PLATFORMS_LAYER],
        #                                     friction=WALL_FRICTION,
        #                                     collision_type="platforms",
        #                                     body_type=arcade.PymunkPhysicsEngine.STATIC
        #                                     )
        self.scene.remove_sprite_list_by_name(PLATFORMS_LAYER)
        self.scene.add_sprite(ENEMIES_LAYER, enemy)
        self.physics_engine.add_sprite_list(self.scene[ENEMIES_LAYER],
                                            friction=0,
                                            mass=PLAYER_MASS,
                                            collision_type="enemy"
                                            )



        # self.physics_engine.add_collision_handler()
        # self.physics_engine.add_collision_handler("enemy", "platform", begin_handler=enemy_platform_jump_collide)
        self.physics_engine.add_collision_handler("enemy", "enemy", begin_handler=enemy_enemy_collide)



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

        enemy : Enemy = None
        object : Object = None
        for enemy in self.scene[ENEMIES_LAYER]:
            if not enemy.has_color:
                objects = arcade.check_for_collision_with_list(enemy, self.scene[OBJECTS_LAYER])
                for object in objects:
                    if object.has_color:
                        enemy.steal(object.color)
                        enemy.change_x = -enemy.change_x
                        object.remove_color()
                        enemy.split()
                        break

        self.physics_engine.step()



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
        enemy: Enemy = self.scene[ENEMIES_LAYER][0]
        if button == arcade.MOUSE_BUTTON_LEFT:

            if enemy.has_color:
                closest_sprite = self.get_closest_colored_sprite(enemy)
                if closest_sprite:
                    closest_sprite.give_color(enemy.color)

            enemy.destroy()
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            enemy.split()

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