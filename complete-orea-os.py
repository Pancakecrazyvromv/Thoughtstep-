import os
import sys
import logging
import subprocess
import requests
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import random

# API Configuration
class APIConfig:
    GEMINI_API_KEY = "your-api-key-here"
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
    
    @classmethod
    def validate_credentials(cls):
        if cls.GEMINI_API_KEY == "your-api-key-here":
            logging.warning("API key not configured! Please update APIConfig class.")
            return False
        return True

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orea_cloud.log'),
        logging.StreamHandler()
    ]
)

class OreaCloudOS:
    def __init__(self):
        self.commands = {
            'help': self.show_help,
            'exit': self.exit_program,
            'ai': self.ai_chat,
            'joke': self.tell_joke,
            'paint': self.launch_paint,
            'clear': self.clear_screen,
            'time': self.show_time
        }
        self.cli = self.CLI(self)
        self.gui = self.GUI(self)

    def show_help(self, *args):
        """Show available commands and their descriptions"""
        help_text = """
Available commands:
- help: Shows this help message
- exit: Exits the program
- ai <prompt>: Chat with Gemini AI
- joke: Tells a random joke
- paint: Launches the Paint application
- clear: Clears the screen
- time: Shows current time
"""
        return help_text.strip()

    def exit_program(self, *args):
        """Exit the program"""
        logging.info("Exiting program")
        sys.exit(0)

    def ai_chat(self, *args):
        """Handle AI chat command"""
        if not args:
            return "Usage: ai <prompt>"
        prompt = " ".join(args)
        response = self.gemini_chat(prompt)
        return response if response else "Failed to get a response from AI"

    def gemini_chat(self, prompt):
        """Chat with Gemini AI"""
        try:
            if not APIConfig.validate_credentials():
                return "Please configure your API credentials in the APIConfig class"
            
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': APIConfig.GEMINI_API_KEY
            }
            
            payload = {
                "contents": [{
                    "parts":[{
                        "text": prompt
                    }]
                }]
            }
            
            response = requests.post(
                APIConfig.GEMINI_API_URL,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                logging.error(f"API Error: {response.status_code} - {response.text}")
                return f"API Error: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Request Error: {str(e)}")
            return f"Connection Error: {str(e)}"
        except Exception as e:
            logging.error(f"Error in AI chat: {str(e)}")
            return None

    def tell_joke(self, *args):
        """Tell a random joke"""
        jokes = [
            "Why don't programmers like nature? It has too many bugs.",
            "Why did the programmer quit his job? Because he didn't get arrays.",
            "What do you call a programmer from Finland? Nerdic."
        ]
        return random.choice(jokes)

    def launch_paint(self, *args):
        """Launch the Paint application"""
        paint_app = self.PaintApp()
        return "Launching Paint..."

    def clear_screen(self, *args):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        return "Screen cleared"

    def show_time(self, *args):
        """Show current time"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    class PaintApp:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("Orea Paint")
            self.setup_ui()
            self.root.mainloop()

        def setup_ui(self):
            """Setup Paint UI"""
            self.canvas = tk.Canvas(self.root, width=800, height=600, bg='white')
            self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
            
            # Tools frame
            tools_frame = ttk.Frame(self.root)
            tools_frame.pack(side=tk.TOP, fill=tk.X)
            
            # Color picker
            self.color = tk.StringVar(value='black')
            ttk.Label(tools_frame, text="Color:").pack(side=tk.LEFT)
            colors = ['black', 'red', 'green', 'blue']
            self.color_menu = ttk.Combobox(tools_frame, textvariable=self.color, values=colors)
            self.color_menu.pack(side=tk.LEFT)
            
            # Brush size
            self.brush_size = tk.IntVar(value=2)
            ttk.Label(tools_frame, text="Size:").pack(side=tk.LEFT)
            self.size_scale = ttk.Scale(tools_frame, from_=1, to=10, variable=self.brush_size, orient=tk.HORIZONTAL)
            self.size_scale.pack(side=tk.LEFT)
            
            # Bind mouse events
            self.canvas.bind('<B1-Motion>', self.paint)
            self.canvas.bind('<ButtonRelease-1>', self.reset)
            
            self.old_x = None
            self.old_y = None

        def paint(self, event):
            """Handle painting"""
            if self.old_x and self.old_y:
                self.canvas.create_line(
                    self.old_x, self.old_y, event.x, event.y,
                    width=self.brush_size.get(),
                    fill=self.color.get(),
                    capstyle=tk.ROUND,
                    smooth=tk.TRUE
                )
            self.old_x = event.x
            self.old_y = event.y

        def reset(self, event):
            """Reset coordinates"""
            self.old_x = None
            self.old_y = None

    class CLI:
        def __init__(self, os_instance):
            self.os = os_instance

        def run(self):
            """Run CLI interface"""
            print("Welcome to Orea Cloud OS! Type 'help' to see available commands.")
            while True:
                try:
                    command = input("> ").strip().split()
                    if not command:
                        continue
                    
                    cmd, *args = command
                    if cmd in self.os.commands:
                        result = self.os.commands[cmd](*args)
                        if result:
                            print(result)
                    else:
                        print(f"Unknown command: {cmd}")
                except Exception as e:
                    logging.error(f"Error executing command: {str(e)}")
                    print(f"Error: {str(e)}")

    class GUI:
        def __init__(self, os_instance):
            self.os = os_instance
            self.root = tk.Tk()
            self.root.title("Orea Cloud OS")
            self.setup_ui()

        def setup_ui(self):
            """Setup GUI interface"""
            # Main frame
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

            # Output text area
            self.output_area = scrolledtext.ScrolledText(main_frame, width=60, height=20)
            self.output_area.grid(row=0, column=0, columnspan=2, pady=5)

            # Input field
            self.input_field = ttk.Entry(main_frame, width=50)
            self.input_field.grid(row=1, column=0, pady=5)

            # Send button
            send_button = ttk.Button(main_frame, text="Send", command=self.process_command)
            send_button.grid(row=1, column=1, pady=5)

            # Bind Enter key
            self.input_field.bind('<Return>', lambda e: self.process_command())

        def process_command(self):
            """Process GUI commands"""
            command = self.input_field.get().strip().split()
            if not command:
                return

            cmd, *args = command
            self.output_area.insert(tk.END, f"> {' '.join(command)}\n")
            
            try:
                if cmd in self.os.commands:
                    result = self.os.commands[cmd](*args)
                    if result:
                        self.output_area.insert(tk.END, f"{result}\n")
                else:
                    self.output_area.insert(tk.END, f"Unknown command: {cmd}\n")
            except Exception as e:
                logging.error(f"Error executing command: {str(e)}")
                self.output_area.insert(tk.END, f"Error: {str(e)}\n")

            self.input_field.delete(0, tk.END)
            self.output_area.see(tk.END)

        def run(self):
            """Run GUI interface"""
            self.root.mainloop()

def main():
    """Main entry point"""
    try:
        # Check API configuration on startup
        if not APIConfig.validate_credentials():
            print("WARNING: API credentials not configured!")
            print("Please update the APIConfig class with your credentials:")
            print("1. Open this file in a text editor")
            print("2. Locate the APIConfig class at the top")
            print("3. Replace 'your-api-key-here' with your actual API key")
            proceed = input("Do you want to continue anyway? (y/n): ")
            if proceed.lower() != 'y':
                sys.exit(1)
        
        os_instance = OreaCloudOS()
        user_choice = input("Do you want to use CLI (c) or GUI (g)? ").lower()
        
        if user_choice == 'c':
            os_instance.cli.run()
        elif user_choice == 'g':
            os_instance.gui.run()
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)
    except Exception as e:
        logging.critical(f"Critical error: {str(e)}")
        print(f"Critical error occurred. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
