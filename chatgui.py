import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
from keras.models import load_model
import json
import random
import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime
import customtkinter as ctk
from typing import Optional, Dict, List
import time

class EnhancedChatbot:
    def __init__(self):
        # Initialize NLP components
        self.lemmatizer = WordNetLemmatizer()
        self.model = load_model('chatbot_model.h5')
        self.intents = json.loads(open('intents.json').read())
        self.words = pickle.load(open('words.pkl', 'rb'))
        self.classes = pickle.load(open('classes.pkl', 'rb'))
        
        # Initialize main window
        self.window = ctk.CTk()
        self.window.title("Nutriscan Chatbot")
        self.window.geometry("1000x700")
        self.window.minsize(800, 600)
        
        # Set theme
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        # Initialize chat history
        self.chat_history: List[Dict] = []
        
        # Set up the GUI
        self.setup_gui()
        
        # Initialize typing animation variables
        self.typing_speed = 0.03
        self.is_typing = False

    def setup_gui(self):
        # Create main container
        self.main_container = ctk.CTkFrame(self.window)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Create header frame
        self.setup_header()
        
        # Create chat area
        self.setup_chat_area()
        
        # Create input area
        self.setup_input_area()
        
        # Create status bar
        self.setup_status_bar()

    def setup_header(self):
        header_frame = ctk.CTkFrame(self.main_container, height=60)
        header_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Nutriscan Chatbot",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        self.settings_btn = ctk.CTkButton(
            header_frame,
            text="⚙️ Settings",
            width=100,
            command=self.show_settings
        )
        self.settings_btn.pack(side=tk.RIGHT, padx=10)

    def setup_chat_area(self):
        # Create chat container
        chat_container = ctk.CTkFrame(self.main_container)
        chat_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create chat display
        self.chat_display = ctk.CTkTextbox(
            chat_container,
            wrap=tk.WORD,
            font=ctk.CTkFont(size=12),
            activate_scrollbars=True,
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_display.configure(state='disabled')
        
        # Configure tags for message styling
        self.chat_display.tag_config(
            "user_message",
            justify='right'
        )
        self.chat_display.tag_config(
            "bot_message",
            justify='left'
        )
        self.chat_display.tag_config("timestamp")

    def setup_input_area(self):
        input_container = ctk.CTkFrame(self.main_container)
        input_container.pack(fill=tk.X, padx=5, pady=5)

        # Suggestion frame
        self.suggestion_frame = ctk.CTkFrame(input_container)
        self.suggestion_frame.pack(fill=tk.X, pady=(0, 5))
        self.update_suggestions([
            "Tell me about career options",
            "What courses should I take?",
            "How to choose a college?"
        ])

        # Input frame
        input_frame = ctk.CTkFrame(input_container)
        input_frame.pack(fill=tk.X)

        # Message input
        self.message_input = ctk.CTkTextbox(
            input_frame,
            height=60,
            wrap=tk.WORD,
            font=ctk.CTkFont(size=12),
            activate_scrollbars=True
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Send button
        self.send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            width=100,
            command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # Bind enter key
        self.message_input.bind("<Return>", self.handle_return)

    def setup_status_bar(self):
        self.status_bar = ctk.CTkLabel(
            self.main_container,
            text="Online",
            font=ctk.CTkFont(size=10)
        )
        self.status_bar.pack(fill=tk.X, padx=5)

    def update_suggestions(self, suggestions: List[str]):
        for widget in self.suggestion_frame.winfo_children():
            widget.destroy()
            
        for suggestion in suggestions:
            btn = ctk.CTkButton(
                self.suggestion_frame,
                text=suggestion,
                height=30,
                command=lambda s=suggestion: self.use_suggestion(s)
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)

    def use_suggestion(self, suggestion: str):
        self.message_input.delete("1.0", tk.END)
        self.message_input.insert("1.0", suggestion)
        self.send_message()

    def show_settings(self):
        settings_window = ctk.CTkToplevel(self.window)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        
        ctk.CTkLabel(settings_window, text="Appearance").pack(pady=10)
        theme_var = tk.StringVar(value=ctk.get_appearance_mode())
        theme_option = ctk.CTkOptionMenu(
            settings_window,
            values=["Light", "Dark", "System"],
            variable=theme_var,
            command=lambda mode: ctk.set_appearance_mode(mode.lower())
        )
        theme_option.pack(pady=5)

    def show_status(self, message: str, duration: int = 3000):
        self.status_bar.configure(text=message)
        self.window.after(duration, lambda: self.status_bar.configure(text="Online"))

    def animate_typing(self, message: str, tag: str):
        if self.is_typing:
            return
            
        self.is_typing = True
        self.chat_display.configure(state='normal')
        
        for char in message:
            self.chat_display.insert(tk.END, char, tag)
            self.chat_display.see(tk.END)
            self.chat_display.update()
            time.sleep(self.typing_speed)
            
        self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.configure(state='disabled')
        self.is_typing = False

    def append_message(self, message: str, sender: str):
        self.chat_display.configure(state='normal')
        timestamp = datetime.now().strftime("%H:%M")
        
        # Add timestamp
        self.chat_display.insert(tk.END, f"{timestamp} - ", "timestamp")
        
        # Add message with appropriate styling
        if sender == "user":
            self.chat_display.insert(tk.END, f"You: {message}\n\n", "user_message")
        else:
            threading.Thread(target=self.animate_typing, args=(f"Bot: {message}", "bot_message")).start()
            
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def handle_return(self, event):
        if not event.state & 0x1:  # If shift is not pressed
            self.send_message()
            return "break"

    def clean_up_sentence(self, sentence: str) -> List[str]:
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words

    def bow(self, sentence: str, words: List[str], show_details: bool = True) -> np.ndarray:
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(words)
        for s in sentence_words:
            for i, w in enumerate(words):
                if w == s:
                    bag[i] = 1
        return np.array(bag)

    def predict_class(self, sentence: str) -> List[Dict]:
        """
        Predict the intent class of a sentence using the trained model.
        Returns a list of intents with their probabilities.
        """
        p = self.bow(sentence, self.words, show_details=False)
        res = self.model.predict(np.array([p]))[0]
        
        ERROR_THRESHOLD = 0.2  # Lowered threshold for short inputs
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        
        if not results:
            # If no intent is confident, return 'unknown' tag
            return [{"intent": "unknown", "probability": "0"}]
        
        return [{"intent": self.classes[r[0]], "probability": str(r[1])} for r in results]


    def get_response(self, ints: List[Dict]) -> str:
        """
        Return a response based on predicted intents.
        If intent is unknown, return a smart fallback.
        """
        if not ints or ints[0]['intent'] == "unknown":
            # Smarter fallback messages
            fallback_messages = [
                "Sorry, I didn't quite understand that. Could you rephrase?",
                "I'm not sure I got that. Do you want help with BMI, SMR, or diet plans?",
                "Hmm, I’m not trained for that query yet. Try typing 'BMI', 'SMR', or 'Diet'."
            ]
            return random.choice(fallback_messages)
        
        tag = ints[0]['intent']
        list_of_intents = self.intents['intents']
        
        for i in list_of_intents:
            if i['tag'] == tag:
                result = random.choice(i['responses'])
                break
        else:
            # In case the tag is not found (extra safety)
            result = "I didn't quite get that. Could you try again?"
        
        return result


    def process_message(self, message: str) -> str:
        ints = self.predict_class(message)
        response = self.get_response(ints)
        return response

    def send_message(self):
        message = self.message_input.get("1.0", tk.END).strip()
        if message:
            self.message_input.delete("1.0", tk.END)
            self.append_message(message, "user")
            
            def get_bot_response():
                response = self.process_message(message)
                self.window.after(0, lambda: self.append_message(response, "bot"))
            
            threading.Thread(target=get_bot_response).start()
            
            # Update suggestions based on context
            self.update_suggestions([
                "Tell me more",
                "How does this help?",
                "What are the requirements?"
            ])

    def run(self):
        # Show initial greeting
        self.append_message("Hello! I'm your Nutriscan Chatbot. How can I help you today?", "bot")
        
        # Start the main loop
        self.window.mainloop()

if __name__ == "__main__":
    chatbot = EnhancedChatbot()
    chatbot.run()