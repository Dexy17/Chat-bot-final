# chat_interface.py
import re
import sys
import os
from functools import partial

# Color handling with fallback
try:
    from colorama import init, Fore, Style
    init()
except ImportError:
    class Fore:
        GREEN = '\033[92m'
        BLUE = '\033[94m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'
    class Style:
        BRIGHT = '\033[1m'
        RESET_ALL = '\033[0m'

class ChatInterface:
    def __init__(self, user_prefix="You: ", bot_prefix="Bot: ", 
                 user_color=Fore.GREEN, bot_color=Fore.BLUE, line_width=80):
        self.user_prefix = user_prefix
        self.bot_prefix = bot_prefix
        self.user_color = user_color
        self.bot_color = bot_color
        self.line_width = line_width

    def chat_print(self, text, prefix=None, color=None):
        """Print formatted chat messages"""
        prefix = prefix or self.bot_prefix
        color = color or self.bot_color
        formatted_text = self._wrap_text(text, prefix)
        print(color + Style.BRIGHT + formatted_text + Style.RESET_ALL)

    def chat_input(self, prompt=None, color=None):
        """Get styled user input"""
        prompt = prompt or self.user_prefix
        color = color or self.user_color
        try:
            user_input = input(color + Style.BRIGHT + prompt + Style.RESET_ALL)
            return user_input.strip()
        except KeyboardInterrupt:
            self._exit_gracefully()

    def clear_chat(self, message="Chat cleared", clear_color=Fore.YELLOW):
        """Clear the terminal and display a message"""
        os.system('cls' if os.name == 'nt' else 'clear')
        if message:
            print(clear_color + message + Style.RESET_ALL)

    def _wrap_text(self, text, prefix):
        words = re.split(r'\s+', text)
        lines = []
        current_line = []
        for word in words:
            if len(' '.join(current_line + [word])) > self.line_width - len(prefix):
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        if current_line:
            lines.append(' '.join(current_line))
        return '\n'.join([f"{prefix if i==0 else ' '*len(prefix)}{line}" 
                        for i, line in enumerate(lines)])

    def _exit_gracefully(self):
        print("\n" + Fore.RED + "Exiting chat..." + Fore.RESET)
        sys.exit(0)

def setup_chat_interface(**kwargs):
    """Initialize and return a configured ChatInterface instance"""
    return ChatInterface(**kwargs)