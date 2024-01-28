from __future__ import annotations

import random
from math import inf
import math

from typing import Optional

import arcade
from arcade.gui import UIManager, UIBoxLayout, UILabel, UITexturePane, UITextArea, UIFlatButton, UIPadding, UIInputText

from Object import Object
from Enemy import Enemy
from Player import Player

SCREEN_WIDTH = 1350
SCREEN_HEIGHT = 765
SCREEN_TITLE = "Color My World"

OBJECTS_LAYER = "objects"
ENEMIES_LAYER = "enemies"
PLAYER_LAYER = "player"
PLATFORMS_LAYER = "platforms"
WALLS_LAYER = "walls"

# Gravity
GRAVITY = 1500
PLAYER_MOVE_FORCE_ON_GROUND = 10000
# Damping - Amount of speed lost per second
DEFAULT_DAMPING = 1.0
PLAYER_DAMPING = 0.06

# Friction between objects
PLAYER_FRICTION = 1.0
WALL_FRICTION = 0.7
DYNAMIC_ITEM_FRICTION = 0.6

# Mass (defaults to 1)
PLAYER_MASS = 2.5

# Keep player from going too fast
PLAYER_MAX_HORIZONTAL_SPEED = 500
PLAYER_MAX_VERTICAL_SPEED = 1300

# Force applied when moving left/right in the air
PLAYER_MOVE_FORCE_IN_AIR = 10000
# Strength of a jump
PLAYER_JUMP_IMPULSE = 2500

MAX_RIGHT = -inf
MAX_LEFT = inf

sound_path = ':resources:/sounds/'
music_path = ':resources:/music/'
class GameView(arcade.View):
    arcade.Sound(f'{music_path}funkyrobot.mp3').play()

    def __init__(self):
        super().__init__()

        arcade.set_background_color(arcade.color.AMAZON)

        self.scene : Optional[arcade.Scene]

        self.physics_engine : Optional[arcade.PymunkPhysicsEngine]
        self.player_sprite: Optional[arcade.Sprite] = None
        # If you have sprite lists, you should create them here,
        # and set them to None

        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False

        self.max_score = 0
        self.score = self.max_score



    def setup(self):
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

        self.physics_engine = arcade.PymunkPhysicsEngine(damping=DEFAULT_DAMPING,
                                                         gravity=(0, -GRAVITY))

        tile_map = arcade.load_tilemap("./resources/kitchen_smalltable.tmj", 0.356, {
            WALLS_LAYER: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "Simple"
            }
        })


        self.scene = arcade.Scene.from_tilemap(tile_map)

        self.create_objects_spritelist("objects0")
        self.create_objects_spritelist("objects2")
        self.create_objects_spritelist("objects1")

        self.max_score = len(self.scene[OBJECTS_LAYER])
        self.score = self.max_score

        self.scene.add_sprite_list(ENEMIES_LAYER, False, arcade.SpriteList())
        enemy = Enemy(center_x=450, center_y=400)
        enemy.color = arcade.color.LIGHT_GRAY
        self.scene.add_sprite(ENEMIES_LAYER, enemy)

        self.scene.add_sprite_list(PLAYER_LAYER, False, arcade.SpriteList())
        self.player_sprite = Player(center_x=600, center_y=100)
        self.scene.add_sprite(PLAYER_LAYER, self.player_sprite)

        self.physics_engine.add_sprite_list(self.scene[WALLS_LAYER],
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)
        self.physics_engine.add_sprite_list(self.scene[PLATFORMS_LAYER],
                                            friction=WALL_FRICTION,
                                            collision_type="platform",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)
        for platform in self.scene[PLATFORMS_LAYER]:
            platform.visible = False

        self.add_enemy_phisics(enemy)

        self.physics_engine.add_sprite(self.player_sprite,
                                        friction=0,
                                        mass=PLAYER_MASS,
                                        collision_type="player",
                                        max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED,
                                        max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                        moment_of_inertia=inf)


        # self.physics_engine.add_collision_handler()
        self.physics_engine.add_collision_handler("player", "platform", begin_handler=enemy_platform_jump_collide)
        self.physics_engine.add_collision_handler("enemy", "platform", begin_handler=enemy_platform_jump_collide)
        self.physics_engine.add_collision_handler("enemy", "enemy", begin_handler=enemy_enemy_collide)
        self.physics_engine.add_collision_handler("enemy", "wall", begin_handler=enemy_wall_collide)
        self.physics_engine.add_collision_handler("enemy", "player", begin_handler=enemy_enemy_collide)

    def add_enemy_phisics(self, enemy):
        self.physics_engine.add_sprite(enemy,
                                       mass=PLAYER_MASS,
                                       collision_type="enemy",
                                       friction=0,
                                       moment_of_inertia=inf,
                                       max_horizontal_velocity=200)

    def create_objects_spritelist(self, layer):
        colors = vars(arcade.color)
        objects = arcade.SpriteList()
        sprites = []

        for sprite in self.scene[layer]:
            o = Object()
            o.texture = sprite.texture
            o.scale = sprite.scale
            o.width = sprite.width
            o.height = sprite.height
            o.center_x = sprite.center_x
            o.center_y = sprite.center_y
            o.angle = sprite.angle
            sprites.append(sprite)
            objects.append(o)
            try:
                o.color = colors[sprite.properties["color"]]
            except KeyError:
                o.color = arcade.color.WHITE
            global MAX_RIGHT
            global MAX_LEFT
            if o.right > MAX_RIGHT:
                MAX_RIGHT = o.right
            if o.left < MAX_LEFT:
                MAX_LEFT = o.left

        for sprite in sprites:
            sprite.remove_from_sprite_lists()

        for object in objects:
            self.scene.add_sprite(OBJECTS_LAYER, object)

    def on_draw(self):
        self.clear()
        self.scene.draw()
        arcade.draw_text(start_x=175, start_y=SCREEN_HEIGHT-50, font_size=18, color=(0,0,0), text=f"{round(self.score / self.max_score * 100, 2)}%")
        arcade.draw_text(start_x=175, start_y=SCREEN_HEIGHT-70, font_size=18, color=(0,0,0), text=f"Sorrows: {Enemy.sprites_number}")
        # change face by score

    def on_update(self, delta_time):
        if Enemy.sprites_number <= 0:
            highscoresView = HighscoresView()
            highscoresView.setup(self.score)
            self.window.show_view(highscoresView)

        self.scene.on_update(delta_time)
        self.player_update(delta_time)
        new_enemies = []

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

        enemies = arcade.check_for_collision_with_list(self.player_sprite, self.scene[ENEMIES_LAYER])
        for enemy in enemies:
            if enemy.has_color:
                self.retrive_color(enemy)
                arcade.Sound(f'{sound_path}hurt5.wav').play()
            enemy.destroy()
            arcade.Sound(f'{sound_path}hurt4.wav').play()

        self.physics_engine.step()

    def move_enemy(self, enemy, delta_time):
        is_on_ground = self.physics_engine.is_on_ground(enemy)
        if is_on_ground:
            enemy.time += delta_time
            if enemy.time > enemy.move_time:
                enemy.time = 0
                jump_chance = random.random()
                if jump_chance < 0.5:
                    self.jump(enemy)
                else:
                    self.walk(enemy)

    def jump(self, enemy):
        if enemy.has_color and random.random() < 0.2:
            if abs(MAX_RIGHT - enemy.center_x) > abs(MAX_LEFT - enemy.center_x):
                jump_angle = random.uniform(-45, 0)
            else:
                jump_angle = random.uniform(0, 45)
            if random.random() < 0.33:
                jump_angle =- jump_angle
        else:
            jump_angle = random.uniform(-45, 45)

        angle_rad = math.radians(jump_angle)
        force = random.uniform(1.5, 2) * GRAVITY
        self.physics_engine.apply_impulse(enemy, (math.sin(angle_rad) * force, math.cos(angle_rad) * force))

    def walk(self, enemy):
        if enemy.has_color and random.random() < 0.2:
            if abs(MAX_RIGHT - enemy.center_x) > abs(MAX_LEFT - enemy.center_x):
                enemy.move_force = -100
            else:
                enemy.move_force = 100
        else:
            enemy.move_force = random.choice([-100, 100])
        self.physics_engine.set_velocity(enemy, (enemy.move_force, self.physics_engine.get_physics_object(enemy).body.velocity[1]))



    def steal_color(self, enemy, color):
        enemy.steal(color)
        self.score -= 1
        for new_enemy in enemy.split():
            self.scene.add_sprite(ENEMIES_LAYER, new_enemy)
            self.add_enemy_phisics(new_enemy)

    def retrive_color(self, enemy):
        self.score += 1
        closest_sprite = self.get_random_colored_sprite(enemy)
        if closest_sprite:
            closest_sprite.give_color(enemy.color)

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
                arcade.Sound(f'{sound_path}jump3.wav').play()
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
        else:
            self.physics_engine.set_horizontal_velocity(self.player_sprite, 0)
            # Player's feet are not moving. Therefore up the friction so we stop.
            self.physics_engine.set_friction(self.player_sprite, 10.0)

        if self.player_sprite.center_x > MAX_RIGHT:
            self.physics_engine.set_position(self.player_sprite, (MAX_RIGHT, self.player_sprite.center_y))
            self.physics_engine.set_velocity(self.player_sprite, (0, 0))
        if self.player_sprite.center_x < MAX_LEFT:
            self.physics_engine.set_position(self.player_sprite, (MAX_LEFT, self.player_sprite.center_y))
            self.physics_engine.set_velocity(self.player_sprite, (0, 0))

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

    def get_random_colored_sprite(self, sprite) -> Object:
        index = random.randint(0, self.score-1)
        closest_sprite = None
        i = 0
        o: Object = None
        for o in self.scene[OBJECTS_LAYER]:
            if i == index:
                return o
            i+=1

class HighscoresView(arcade.View):
    def __init__(self):
        super().__init__()

        arcade.set_background_color(arcade.color.AO)

        self.score = 0
        self.user_name_input = UIInputText(width=200, height=50, text="Name", text_color=arcade.color.BLACK)

    def setup(self, score):
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

        self.score = score
        arcade.set_background_color(arcade.color.AO)
        self.manager = UIManager()
        self.manager.enable()

        self.layout = UIBoxLayout(x=200, y=600, align="center")
        self.manager.add(self.layout)

        self.layout.add(UILabel(text="Highscores", font_size=18, bold=True))

        self.text_area = UITextArea(x=100, y=100, width=200, height=200)
        self.text_area.text = self.reload_text()

        bg_tex = arcade.load_texture(":resources:gui_basic_assets/window/grey_panel.png")
        text_area = UITextArea(width=200,
                               height=300,
                               text=self.text,
                               text_color=(0, 0, 0, 255),
                               bg_tex=bg_tex)

        newHighscorePanel =  UITexturePane(
                text_area.with_space_around(right=50),
                tex=bg_tex,
                padding=(10, 10, 10, 10)
        )

        self.layout.add(newHighscorePanel)

        self.inputPanel = UIBoxLayout()
        self.inputPanel.add(UILabel(text=f"Congrats, you'v achieved an highscore ({self.score}%)! Enter your name:", font_size=14, bold=True))
        self.inputPanel.add(self.user_name_input)

        button = UIFlatButton(text="OK", width=200)
        button.on_click = self.save_highscores
        self.inputPanel.add(button)

        if score > self.scores[-1][1]:
            self.layout.add(
                self.inputPanel
            )

        reloadButton = UIFlatButton(text="Play again", width=200)
        reloadButton.on_click = self.reload

        self.layout.add(UIPadding(reloadButton, padding=(20, 20, 20, 20)))


    def save_highscores(self, event):
        file = open('./resources/highscores.csv', 'w')
        self.scores.append((self.user_name_input.text, self.score))
        self.scores.sort(reverse=True, key=lambda x: x[1])
        for (user, points) in self.scores[:10]:
            file.write(f'{user};{points}\n')
        file.close()
        self.layout.remove(self.inputPanel)

    def reload_text(self):
        file = open('./resources/highscores.csv')
        self.scores = []
        for line in file:
            user, points = line.strip().split(';')
            self.scores.append(line.strip().split(';'))
        file.close()

        self.scores = [(user, float(points)) for (user, points) in self.scores]
        self.text = ''
        i = 1
        for (user, points) in self.scores:
            self.text += (f'{i}. {user}\t{str(points)}\n')
            i += 1
        return self.text

    def reload(self, event):
        gameView = GameView()
        gameView.setup()
        self.window.show_view(gameView)
    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_update(self, delta_time: float):
        self.manager.on_update(delta_time)


def main():
    """ Main function """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = GameView()
    start_view.setup()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()