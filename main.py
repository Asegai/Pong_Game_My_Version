from kivy.app import App
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

star_image_path = "C:/Users/aesas/Desktop/app_test_2/star.png"
explosion_image_path = "C:/Users/aesas/Desktop/app_test_2/explosion.png"

Builder.load_string(f'''
<PongBall>:
    size: 50, 50
    canvas:
        Ellipse:
            pos: self.pos
            size: self.size

<PongPaddle>:
    size: 25, 200
    canvas:
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
        text: str(root.player1.score)
        font_size: 30
        center_x: root.width / 4
        top: root.top - 10

    Label:
        id: player2_score_label
        text: str(root.player2.score)
        font_size: 30
        center_x: root.width * 3 / 4
        top: root.top - 10
''')

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset

class RainbowStar(Image):
    def __init__(self, **kwargs):
        super(RainbowStar, self).__init__(**kwargs)
        self.star_image = True

    def update_image(self, *args):
        if self.star_image and self.center_y <= self.parent.height / 2:
            self.source = explosion_image_path
            self.star_image = False

class PongGame(Widget):
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

        # bounce off paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # bounce off top and bottom
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1

        
        if self.ball.x < 0:
            self.player2.score += 1
            self.check_for_star()
            self.serve_ball(vel=(4, 0))
        if self.ball.right > self.width:
            self.player1.score += 1
            self.check_for_star()
            self.serve_ball(vel=(-4, 0))

        self.player1_score.text = str(self.player1.score)
        self.player2_score.text = str(self.player2.score)

        # AI for the right paddle
        if self.ball.center_y > self.player2.center_y:
            self.player2.center_y += min(self.ball.center_y - self.player2.center_y, 4)
        if self.ball.center_y < self.player2.center_y:
            self.player2.center_y -= min(self.player2.center_y - self.ball.center_y, 4)

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y

    def check_for_star(self):
        if (self.player1.score % 5 == 0 or self.player2.score % 5 == 0) and (self.player1.score > 0 or self.player2.score > 0):
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

class MainMenu(RelativeLayout):
    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)
        self.label = Label(text='Hello the World', font_size=24, size_hint=(None, None), size=(300, 100),
                           pos_hint={'center_x': 0.5, 'center_y': 0.7})
        self.button = Button(text='World', size_hint=(None, None), size=(150, 40),
                             pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.button.bind(on_press=self.start_game)
        
        self.add_widget(self.label)
        self.add_widget(self.button)
    
    def start_game(self, instance):
        self.clear_widgets()
        self.game = PongGame()
        self.add_widget(self.game)
        self.game.serve_ball()
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)

class PongApp(App):
    def build(self):
        return MainMenu()

if __name__ == '__main__':
    PongApp().run()
