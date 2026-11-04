
import tkinter as tk
from tkinter import messagebox

# Create the main window
root = tk.Tk()
root.title("Hello Tkinter - Dechen Choden")
root.geometry("400x250")

# Create heading
heading = tk.Label(
    root,
    text="Hello, Welcome to Tkinter!",
    font=("Arial", 16, "bold")
)
heading.pack(pady=30)

# Button function
def button_clicked():
    messagebox.showinfo(
        "Success",
        "Button Clicked!"
    )

# Create button
button = tk.Button(
    root,
    text="Click Me",
    command=button_clicked
)
button.pack(pady=20)

# Run application
root.mainloop()
