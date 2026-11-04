
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup


class HelloKivyApp(App):

    def build(self):

        # Set window title
        self.title = "Hello Kivy - Dechen Choden"

        # Create main layout
        layout = BoxLayout(
            orientation="vertical",
            padding=40,
            spacing=30
        )

        # Create heading
        heading = Label(
            text="Hello, Welcome to Kivy!",
            font_size=24,
            bold=True
        )

        # Create button
        button = Button(
            text="Click Me",
            size_hint=(1, 0.25)
        )

        # Connect button to function
        button.bind(on_press=self.button_clicked)

        # Add widgets to layout
        layout.add_widget(heading)
        layout.add_widget(button)

        return layout

    def button_clicked(self, instance):

        # Create popup
        popup = Popup(
            title="Success",
            content=Label(
                text="Button Clicked!"
            ),
            size_hint=(0.7, 0.3)
        )

        popup.open()


# Run application
if __name__ == "__main__":
    HelloKivyApp().run()
