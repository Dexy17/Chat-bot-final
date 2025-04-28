def run_with_gui(gui):
    name = gui.get_input("Enter your name: ")
    gui.chat_print(f"Hello, {name}!", sender="bot")

    color = gui.get_input("What's your favorite color?")
    gui.chat_print(f"{color} is a nice color!", sender="bot")
