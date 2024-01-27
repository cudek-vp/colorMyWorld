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
from Enemy import Enemy
from Player import Player

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Starting Template"

OBJECTS_LAYER = "objects0"
ENEMIES_LAYER = "enemies"
PLAYER_LAYER = "player"
PLATFORMS_LAYER = "platforms"
WALLS_LAYER = "walls"

# Gravity
GRAVITY = 1500
PLAYER_MOVE_FORCE_ON_GROUND = 8000
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

# Force applied when moving left/right in the air
PLAYER_MOVE_FORCE_IN_AIR = 900
# Strength of a jump
PLAYER_JUMP_IMPULSE = 1800

class Game(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        self.scene : Optional[arcade.Scene]

        self.physics_engine : Optional[arcade.PymunkPhysicsEngine]
        self.player_sprite: Optional[arcade.Sprite] = None
        # If you have sprite lists, you should create them here,
        # and set them to None

        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.setup()



    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        # Create your sprites and sprite lists here
        layer_options = {
            WALLS_LAYER: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "Simple"
            }
        }


        self.tile_map = arcade.load_tilemap("./resources/kitchen.tmj", 0.2, layer_options)
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
        enemy = Enemy(center_x=450, center_y=400)
        enemy.color = arcade.color.LIGHT_GRAY

        def enemy_platform_jump_collide(enemy, _platform, _arbiter, _space, _data):
            po : arcade.PymunkPhysicsObject = self.physics_engine.get_physics_object(enemy)
            return po.body.velocity[1] < 0

        def enemy_enemy_collide(_enemy1, _enemy2, _arbiter, _space, _data):
            return False

        def enemy_wall_collide(enemy, _wall, _arbiter, _space, _data):
            enemy.move_force = -enemy.move_force
            enemy.change_y = 0
            enemy.set_position(enemy.center_x, enemy.center_y+100)
            return True

        def player_wall_collide(player, _wall, _arbiter, _space, _data):

            player.change_y = 0
            return True

        self.physics_engine.add_sprite_list(self.scene[WALLS_LAYER],
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)
        # self.physics_engine.add_sprite_list(self.scene[PLATFORMS_LAYER],
        #                                     friction=WALL_FRICTION,
        #                                     collision_type="platforms",
        #                                     body_type=arcade.PymunkPhysicsEngine.STATIC
        #                                     )
        self.scene.add_sprite(ENEMIES_LAYER, enemy)
        self.physics_engine.add_sprite_list(self.scene[ENEMIES_LAYER],
                                            mass=PLAYER_MASS,
                                            collision_type="enemy"
                                            )



        # self.physics_engine.add_collision_handler()
        # self.physics_engine.add_collision_handler("enemy", "platform", begin_handler=enemy_platform_jump_collide)
        self.physics_engine.add_collision_handler("enemy", "enemy", begin_handler=enemy_enemy_collide)
        self.physics_engine.add_collision_handler("enemy", "wall", begin_handler=enemy_wall_collide)
        self.physics_engine.add_collision_handler("enemy", "player", begin_handler=enemy_enemy_collide)

        self.scene.add_sprite_list(PLAYER_LAYER, False, arcade.SpriteList())
        self.player_sprite = Player(center_x=450, center_y=400)
        self.scene.add_sprite(PLAYER_LAYER, self.player_sprite)
        # player.color = arcade.color.LIGHT_GRAY

        self.physics_engine.add_sprite_list(self.scene[PLAYER_LAYER],
                                            friction=0,
                                            mass=PLAYER_MASS,
                                            collision_type="player"
                                            )

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
        self.player_update(delta_time)
        new_enemies = []

        enemy : Enemy = None
        object : Object = None
        for enemy in self.scene[ENEMIES_LAYER]:
            self.move_enemy(enemy, delta_time)
            if not enemy.has_color:
                objects = arcade.check_for_collision_with_list(enemy, self.scene[OBJECTS_LAYER])
                for object in objects:
                    if object.has_color:
                        self.steal_color(enemy, object.color)
                        enemy.change_x = -enemy.change_x
                        object.remove_color()
                        break

        self.physics_engine.step()

    def move_enemy(self, enemy, delta_time):
        enemy.time += delta_time
        if enemy.time > enemy.move_time:
            enemy.time = 0
            enemy.move_force = random.choice([-100, 100])
        self.physics_engine.set_velocity(enemy, (enemy.move_force, self.physics_engine.get_physics_object(enemy).body.velocity[1]))



    def steal_color(self, enemy, color):
        enemy.steal(color)
        for new_enemy in enemy.split():
            self.scene.add_sprite(ENEMIES_LAYER, new_enemy)
            self.physics_engine.add_sprite(new_enemy, friction=0,
                                                mass=2.5,
                                                collision_type="enemy")

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            self.up_pressed = True
            # find out if player is standing on ground, and not on a ladder
            if self.physics_engine.is_on_ground(self.player_sprite):
                impulse = (0, PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False

    # def on_key_press(self, key, modifiers):
    #     """Called whenever a key is pressed. """
    #     if key == arcade.key.LEFT:
    #         self.left_pressed = True
    #     elif key == arcade.key.RIGHT:
    #         self.right_pressed = True
    #     elif key == arcade.key.UP:
    #         # find out if player is standing on ground
    #         if self.physics_engine.is_on_ground(self.player_sprite):
    #             self.right_pressed = False

    def player_update(self, delta_time):
        """ Movement and game logic """

        is_on_ground = self.physics_engine.is_on_ground(self.player_sprite)
        # Update player forces based on keys pressed
        if self.left_pressed and not self.right_pressed:
            # Create a force to the left. Apply it.
            if is_on_ground:
                force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (-PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:
            # Create a force to the right. Apply it.
            if is_on_ground:
                force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player_sprite, 0)


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