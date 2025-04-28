import tkinter as tk
from tkinter import ttk
from googletrans import Translator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import SchemeMap, SCHEMES, transliterate

class ChatApp(tk.Tk):
    def __init__(self, logic=None, flow=[]):
        super().__init__()
        self.title("ChatBot GUI")
        self.configure(bg="#f0f0f0")
        self.logic = logic
        self.flow = flow

        # Setup translator and supported languages
        self.translator = Translator()
        self.supported_languages = {
            'Auto Detect': None,
            'English': 'en',
            'Hindi': 'hi',
            'Hinglish': 'hi',  # Latin-script Hindi pronunciation
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
        }
        self.selected_lang = tk.StringVar(value='English')
        self.last_user_lang = None

        self.user_response = tk.StringVar()
        self._build_widgets()
        self._on_send_clicked = lambda: None

        # Schedule initial logic run, store after id for cancellation
        if self.logic:
            self._logic_after_id = self.after(300, self._start_logic)

    def _start_logic(self):
        if self.logic:
            self.logic(self)

    def destroy(self):
        # Cancel pending logic callbacks before destroying
        try:
            if hasattr(self, '_logic_after_id') and self._logic_after_id:
                self.after_cancel(self._logic_after_id)
        except Exception:
            pass
        super().destroy()

    def _build_widgets(self):
        header = ttk.Frame(self, padding=5)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)
        ttk.Label(header, text="Language:").grid(row=0, column=0, sticky="w")
        lang_menu = ttk.Combobox(
            header,
            textvariable=self.selected_lang,
            values=list(self.supported_languages.keys()),
            state="readonly",
            width=15
        )
        lang_menu.grid(row=0, column=1, sticky="w")
        lang_menu.bind("<<ComboboxSelected>>", self._on_language_change)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.chat_frame = ttk.Frame(self)
        self.chat_frame.grid(row=1, column=0, sticky="nsew")
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.chat_canvas = tk.Canvas(self.chat_frame, bg="#f0f0f0", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.chat_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.chat_canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )
        self.canvas_window = self.chat_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.chat_canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_canvas.bind("<Configure>", self._resize_canvas)

        self.input_frame = ttk.Frame(self, padding=5)
        self.input_frame.grid(row=2, column=0, sticky="ew")
        self.input_frame.columnconfigure(0, weight=1)
        self.user_input = ttk.Entry(self.input_frame, textvariable=self.user_response, font=("Helvetica", 14))
        self.user_input.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.user_input.bind("<Return>", lambda e: self._on_send_clicked())
        self.send_button = ttk.Button(self.input_frame, text="Send", command=lambda: self._on_send_clicked())
        self.send_button.grid(row=0, column=1, padx=5, pady=5)

    def _on_language_change(self, event=None):
        self.reset_chat()
        self.last_user_lang = None
        # Cancel any pending logic call and reschedule
        try:
            if hasattr(self, '_logic_after_id') and self._logic_after_id:
                self.after_cancel(self._logic_after_id)
        except Exception:
            pass
        if self.logic:
            self._logic_after_id = self.after(100, self._start_logic)

    def _resize_canvas(self, event):
        self.chat_canvas.itemconfig(self.canvas_window, width=event.width)

    def _add_message(self, text, sender="user"):
        bubble = ttk.Label(
            self.scrollable_frame,
            text=text,
            background="#cce5ff" if sender == "user" else "#e6e6e6",
            anchor="e" if sender == "user" else "w",
            wraplength=300,
            padding=8,
            relief="ridge"
        )
        bubble.pack(anchor="e" if sender == "user" else "w", pady=2, padx=10)
        self.after(100, lambda: self.chat_canvas.yview_moveto(1.0))

    def _translate_text(self, text, dest, use_pronunciation=False):
        try:
            tr = self.translator.translate(text, dest=dest)
            if use_pronunciation:
                return tr.pronunciation or tr.text
            return tr.text
        except Exception:
            return text

    def _add_bot_message(self, text):
        key = self.selected_lang.get()
        to_translate = text
        if key == 'Hinglish':
            to_translate = self._translate_text(text, 'hi')
            to_translate = transliterate(to_translate, sanscript.DEVANAGARI, sanscript.ITRANS)
        elif key == 'Auto Detect' and self.last_user_lang:
            to_translate = self._translate_text(text, self.last_user_lang)
        else:
            dest = self.supported_languages.get(key)
            if dest:
                to_translate = self._translate_text(text, dest)
        self._add_message(to_translate, sender="bot")

    def _add_bot_message_dynamic(self, text):
        self._add_bot_message(text)

    def prt_bot(self, text: str):
        self._add_bot_message(text)

    def ask_user(self, question: str):
        self._add_bot_message(question)
        self.response_var = tk.StringVar()

        def on_response(event=None):
            raw = self.user_input.get().strip()
            if not raw:
                return
            self._add_message(raw, sender="user")
            self.user_input.delete(0, tk.END)
            key = self.selected_lang.get()
            src = self.supported_languages.get(key)
            if src is None:
                detected = self.translator.detect(raw).lang
                if detected in self.supported_languages.values():
                    src = detected
            try:
                tr = self.translator.translate(raw, src=src or 'en', dest='en')
                self.response_var.set(tr.text)
                self.last_user_lang = detected if src is None else self.last_user_lang
            except Exception:
                self._add_bot_message("I am sorry, I could not understand. Please reply in a supported language.")

        self.user_input.bind("<Return>", on_response)
        self._on_send_clicked = on_response
        self.wait_variable(self.response_var)
        return self.response_var.get()

    def ask_user_dynamic(self, question: str):
        lng = self.selected_lang.get()
        if lng != "Auto Detect":
            print(lng)
            return self.ask_user(question)
        else:
            self._add_bot_message(question)
            self.response_var = tk.StringVar()
            def on_response(event=None):
                raw = self.user_input.get().strip()
                if not raw:
                    return
                self._add_message(raw, sender="user")
                self.user_input.delete(0, tk.END)
                detected = self.translator.detect(raw).lang
                if detected in self.supported_languages.values():
                    self.last_user_lang = detected
                    tr = self.translator.translate(raw, src=detected, dest='en')
                    self.response_var.set(tr.text)
                else:
                    self._add_bot_message("I am sorry, I could not understand. Please reply in a supported language.")

            self.user_input.bind("<Return>", on_response)
            self._on_send_clicked = on_response
            self.wait_variable(self.response_var)
            return self.response_var.get()

    def ask_user_direct(self, question: str) -> str:
        self._add_bot_message(question)
        self.direct_var = tk.StringVar()

        def on_response(event=None):
            raw = self.user_input.get().strip()
            if not raw:
                return
            self._add_message(raw, sender="user")
            self.user_input.delete(0, tk.END)
            self.direct_var.set(raw)

        self.user_input.bind("<Return>", on_response)
        self._on_send_clicked = on_response
        self.wait_variable(self.direct_var)
        return self.direct_var.get()

    def ask_user_no_translate(self, question: str) -> str:
        self._add_bot_message(question)
        self.no_translate_var = tk.StringVar()

        def on_response(event=None):
            raw = self.user_input.get().strip()
            if not raw:
                return
            self._add_message(raw, sender="user")
            self.user_input.delete(0, tk.END)
            self.no_translate_var.set(raw)

        self.user_input.bind("<Return>", on_response)
        self._on_send_clicked = on_response
        self.wait_variable(self.no_translate_var)
        return self.no_translate_var.get()

    def ask_password(self, prompt: str):
        self._add_bot_message(prompt)
        self.password_var = tk.StringVar()

        def on_password_submit(event=None):
            pwd = self.user_input.get()
            if not pwd:
                return
            self.user_input.delete(0, tk.END)
            self.password_var.set(pwd)

        self.user_input.configure(show="*")
        self.user_input.bind("<Return>", on_password_submit)
        self._on_send_clicked = on_password_submit
        self.wait_variable(self.password_var)
        password = self.password_var.get()
        self.user_input.configure(show="")
        self.user_response.set("")
        return password

    def reset_chat(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
