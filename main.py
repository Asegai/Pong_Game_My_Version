from kivy.app import App
from kivy.uix.label import Label

class class_Test(App):
    def build(self):
        return Label(text='Worlding the Hello')

if __name__ == '__main__':
    class_Test().run()