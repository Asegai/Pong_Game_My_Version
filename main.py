from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout

class class_Test(App):
    def build(self):
        main_layout = RelativeLayout()

        # larger font size
        label = Label(text='Hello the World', font_size=24, size_hint=(None, None), size=(300, 100),
                      pos_hint={'center_x': 0.5, 'center_y': 0.7}) 

        # Button right under the label, centered
        button = Button(text='World', size_hint=(None, None), size=(150, 40),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5})  # Centered

        main_layout.add_widget(label)
        main_layout.add_widget(button)

        return main_layout

if __name__ == '__main__':
    class_Test().run()
