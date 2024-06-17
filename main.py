from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class class_Test(App):
    def build(self):
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        label = Label(text='Hello the World', size_hint=(1, 0.8))  
        
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None)) 
        
        # the button isn't centered
        #! Center button!
    

        button = Button(text='World', size_hint=(None, None), size=(100, 50))

        button_layout.add_widget(BoxLayout())  
        button_layout.add_widget(button)
        button_layout.add_widget(BoxLayout())  

        main_layout.add_widget(label)
        main_layout.add_widget(button_layout)

        return main_layout

if __name__ == '__main__':
    class_Test().run()
