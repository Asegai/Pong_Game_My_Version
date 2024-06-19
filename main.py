from kivy.app import App
from kivy.graphics import Color
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivy.properties import ListProperty
from kivy.core.audio import SoundLoader
from kivy.uix.slider import Slider
from kivy.graphics import Color, Line
import os 




current_dir = os.path.dirname(os.path.realpath(__file__))

star_image_path = os.path.join(current_dir, 'star.png').replace('\\', '/')
explosion_image_path = os.path.join(current_dir, 'explosion.png').replace('\\', '/')
bounce_sound_path = os.path.join(current_dir, 'bounce.mp3').replace('\\', '/')
font_os_path = os.path.join(current_dir, 'pixel.ttf').replace('\\', '/')
game_music_path = os.path.join(current_dir, 'game_music.mp3').replace('\\', '/')
main_menu_music_path = game_music_path #! temporary fix
bounce_sound = SoundLoader.load(bounce_sound_path)
LabelBase.register(name='Pixel', fn_regular=font_os_path)

kv_string = f"""
<Image>:
    source: '{star_image_path}'
"""

Builder.load_string(kv_string)

star_image = Image(source=star_image_path)
explosion_image = Image(source=explosion_image_path)



Builder.load_string(f'''
<PongBall>:
    size: 50, 50
    canvas:
        Ellipse:
            pos: self.pos
            size: self.size

<PongPaddle>:
    color: 1, 1, 1, 1
    size: 25, 200
    canvas:
        Color:
            rgba: self.color
        Rectangle:
            pos: self.pos
            size: self.size

<RainbowStar>:
    source: '{star_image_path}'

<PongGame>:
    ball: pong_ball
    player1: left_paddle
    player2: right_paddle
    player1_score: player1_score_label
    player2_score: player2_score_label

    PongBall:
        id: pong_ball
        center: self.center

    PongPaddle:
        id: left_paddle
        x: root.x
        center_y: root.center_y

    PongPaddle:
        id: right_paddle
        x: root.width - self.width
        center_y: root.center_y

    Label:
        id: player1_score_label
        text: str(root.user_score)
        font_size: 30
        font_name: 'Pixel'
        center_x: root.width / 4
        top: root.top - 10

    Label:
        text: 'You'
        font_size: 20
        font_name: 'Pixel'
        center_x: root.width / 4
        y: player1_score_label.y - player1_score_label.height

    Label:
        id: player2_score_label
        text: str(root.player2.score)
        font_size: 30
        font_name: 'Pixel'
        center_x: root.width * 3 / 4
        top: root.top - 10

    Label:
        text: 'Opponent'
        font_size: 20
        font_name: 'Pixel'
        center_x: root.width * 3 / 4
        y: player2_score_label.y - player2_score_label.height
        
''')

class RainbowButton(Button):
    outline_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super(RainbowButton, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas, outline_color=self.update_canvas)
        self.flash_color()

    def flash_color(self):
        anim = Animation(outline_color=[1, 0, 0, 1]) + Animation(outline_color=[0, 1, 0, 1]) + Animation(outline_color=[0, 0, 1, 1])
        anim.repeat = True
        anim.start(self)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.outline_color)
            Line(width=2, rectangle=(self.x, self.y, self.width, self.height))

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class PongPaddle(Widget):
    score = NumericProperty(0)
    color = ListProperty([1, 1, 1, 1])
    def flash_color(self):
        anim = Animation(color=[1, 0, 0, 1]) + Animation(color=[0, 1, 0, 1]) + Animation(color=[0, 0, 1, 1])
        anim.repeat = True
        anim.start(self)


    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset

            bounce_sound.play()
            Clock.schedule_once(lambda dt: bounce_sound.stop(), 1)

class RainbowStar(Image):
    def __init__(self, **kwargs):
        super(RainbowStar, self).__init__(**kwargs)
        self.star_image = True

    def update_image(self, *args):
        if self.star_image and self.center_y <= self.parent.height / 2:
            self.source = explosion_image_path
            self.star_image = False

class PongGame(Widget):

    def __init__(self, **kwargs):
            super(PongGame, self).__init__(**kwargs)
            # Load and play the game music
            self.music = SoundLoader.load(game_music_path)
            if self.music:
                self.music.loop = True
                self.music.play()

    user_score = NumericProperty(0)
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    player1_score = ObjectProperty(None)
    player2_score = ObjectProperty(None)
    star = None

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):
        self.ball.move()

         
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

       
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1

        
        if self.ball.x < 0:
            self.player2.score += 1
            self.serve_ball(vel=(4, 0))
            self.check_for_star()

       
        if self.ball.right > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, 0))
            self.check_for_star()

       
        if self.player1.x > self.player2.x:
            self.player1_score.text = str(self.player2.score)
            self.player2_score.text = str(self.player1.score)
        else:
            self.player1_score.text = str(self.player1.score)
            self.player2_score.text = str(self.player2.score)

       
        speeds = [dt * 100, dt * 300, dt * 600]
        speed = speeds[int(self.parent.difficulty_slider.value) - 1]
        if self.ball.center_y > self.player2.center_y:
            self.player2.center_y += min(self.ball.center_y - self.player2.center_y, speed)
        if self.ball.center_y < self.player2.center_y:
            self.player2.center_y -= min(self.player2.center_y - self.ball.center_y, speed)

    def on_touch_move(self, touch):
        if self.player1.x < self.width / 2:  
            if touch.x < self.width / 3:
                self.player1.center_y = touch.y
        else:  
            if touch.x > self.width * 2 / 3:
                self.player1.center_y = touch.y

    def check_for_star(self):
        if (self.player1.score + self.player2.score) % 5 == 0 and (self.player1.score >= 0 or self.player2.score >= 0):
            self.spawn_star()

    def spawn_star(self):
        if not self.star:
            self.star = RainbowStar()
            self.add_widget(self.star)
            self.star.center = (self.width / 2, self.height)
            anim = Animation(center_y=self.height / 2, duration=2)
            anim.bind(on_complete=self.explode_star)
            anim.start(self.star)

    def explode_star(self, *args):
        if self.star:
            self.star.source = explosion_image_path
            Clock.schedule_once(self.remove_star, 1.7)

    def update_star_image(self, dt):
        if self.star:
            self.star.update_image()
            Clock.schedule_once(self.remove_star, 0.5)

    def remove_star(self, dt):
        if self.star:
            self.remove_widget(self.star)
            self.star = None
            self.swap_sides()

    def swap_sides(self):
        self.player1.x, self.player2.x = self.player2.x, self.player1.x
        self.player1.center_y, self.player2.center_y = self.player2.center_y, self.player1.center_y

       
        self.player1.score, self.player2.score = self.player2.score, self.player1.score

       
        self.player1_score.text = str(self.player1.score)
        self.player2_score.text = str(self.player2.score)

class MainMenu(RelativeLayout):
    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)

        self.music = SoundLoader.load(main_menu_music_path)

        if self.music:
            self.music.loop = True
            self.music.play()

        self.label = Label(text='Hello the World', font_size=24, font_name='Pixel', size_hint=(None, None), size=(300, 100),
                           pos_hint={'center_x': 0.5, 'center_y': 0.7})
        self.button = RainbowButton(text='World', font_name='Pixel', size_hint=(None, None), size=(150, 40),
                             pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.button.bind(on_press=self.start_game)

        self.difficulty_label = Label(text='Difficulty ', font_name='Pixel', size_hint=(None, None), size=(150, 40),
                                      pos_hint={'center_x': 0.5, 'center_y': 0.437})

        self.difficulty_slider = Slider(min=1, max=3, value=2, step=1, size_hint=(None, None), size=(150, 40),
                                        pos_hint={'center_x': 0.5, 'center_y': 0.4})

        
        self.easy_label = Label(text='Easy', font_name='Pixel', size_hint=(None, None), size=(50, 40))
        self.hard_label = Label(text='Hard', font_name='Pixel', size_hint=(None, None), size=(50, 40))

        self.difficulty_slider.bind(pos=self.update_label_positions)

        self.add_widget(self.label)
        self.add_widget(self.button)
        self.add_widget(self.difficulty_label)
        self.add_widget(self.difficulty_slider)
        self.add_widget(self.easy_label) 
        self.add_widget(self.hard_label)

    def update_label_positions(self, instance, value):
        self.easy_label.pos_hint = {'center_x': (instance.x - 17 ) / instance.parent.width, 'center_y': 0.4}
        self.hard_label.pos_hint = {'center_x': (instance.right + 17 ) / instance.parent.width, 'center_y': 0.4}

    def start_game(self, instance):
        self.clear_widgets()
        self.game = PongGame()
        self.game.player1.flash_color()
        self.add_widget(self.game)
        self.game.serve_ball()

        Clock.schedule_interval(self.game.update, 1.0 / 60.0 / self.difficulty_slider.value)  
    
    def start_game(self, instance):

        if self.music:
            self.music.stop()

        self.clear_widgets()
        self.game = PongGame()
        self.game.player1.flash_color()  
        self.add_widget(self.game)
        self.game.serve_ball()
        
        Clock.schedule_interval(self.game.update, 1.0 / 60.0 / self.difficulty_slider.value)

class PongApp(App):
    def build(self):
        return MainMenu()

if __name__ == '__main__':
    PongApp().run()
