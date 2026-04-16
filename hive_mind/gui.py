import tkinter as tk
from tkinter import scrolledtext, ttk, Canvas, END, messagebox
import threading
import time
from gtts import gTTS
import tempfile
import os
import requests
import playsound

class VoiceInterface:
    def __init__(self, lang='en'):
        self.lang = lang

    def speak(self, text):
        def _play():
            try:
                tts = gTTS(text=text, lang=self.lang)
                with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    playsound.playsound(fp.name)
            except Exception as e:
                print(f"[VoiceInterface] Error: {e}")
        threading.Thread(target=_play, daemon=True).start()

class MemoryVisualizer(tk.Toplevel):
    def __init__(self, master, memory):
        super().__init__(master)
        self.title("STARLITE Memory Core")
        self.geometry("800x600")
        self.configure(bg="#0a0a2a")

        self.text = scrolledtext.ScrolledText(self, wrap=tk.WORD, bg="#1a1a3a", fg="#00ffff", font=("Consolas", 12))
        self.text.pack(fill=tk.BOTH, expand=True)

        self.load_memory(memory)

    def load_memory(self, memory):
        self.text.insert(END, "=== Conversations ===\n")
        for convo in memory.data["conversations"]:
            self.text.insert(END, f"User: {convo['user']}\nAI: {convo['ai']}\n\n")

        self.text.insert(END, "\n=== Symbols ===\n")
        for k, v in memory.data["symbols"].items():
            self.text.insert(END, f"{k}: {v}\n")

        self.text.insert(END, "\n=== Tasks ===\n")
        for task in memory.data["tasks"]:
            self.text.insert(END, f"- {task}\n")

class STARLITEGUI:
    def __init__(self, master, hive_mind):
        self.master = master
        self.hive_mind = hive_mind
        self.hive_mind.app = self
        self.master.title(f"{self.hive_mind.agents[0].identity.name}: OMNI-SUPRA AI HIVE MIND")
        self.master.geometry("1280x720")
        self.master.configure(bg="#001a2a")

        self.ollama_status_cache = {'status': None, 'last_checked': 0}
        self.loading_message_id = None
        self.voice_interface = VoiceInterface(lang='en')

        self.top_frame = tk.Frame(self.master, bg="#001a2a")
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.stargate_canvas = Canvas(self.top_frame, width=200, height=200, bg="#001a2a", highlightthickness=0)
        self.stargate_canvas.pack(side=tk.LEFT, padx=10, pady=10)
        self.stargate_circle = self.stargate_canvas.create_oval(10, 10, 190, 190, outline="#5a8c9a", width=5)
        self.stargate_event_horizon = self.stargate_canvas.create_oval(70, 70, 130, 130, fill="#000000", outline="#00aaff", width=2)

        self.status_frame = tk.Frame(self.top_frame, bg="#001a2a")
        self.status_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self.agent_labels = {}
        for i, agent in enumerate(self.hive_mind.agents):
            label = tk.Label(self.status_frame, text=f"{agent.personality['name']}: Ready", bg="#001a2a", fg="#00ffff", font=("Consolas", 10))
            label.pack(anchor=tk.W, pady=2)
            self.agent_labels[agent.personality['name']] = label

        self.chat_frame = tk.Frame(self.master, bg="#001a2a")
        self.chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10)

        self.conversation_area = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, bg="#002a3a", fg="#aaffff", font=("Consolas", 12), state='disabled', padx=10, pady=10)
        self.conversation_area.pack(fill=tk.BOTH, expand=True)
        self.conversation_area.tag_config('user', foreground='#FFFFFF')
        self.conversation_area.tag_config('ai', foreground='#00FFFF')
        self.conversation_area.tag_config('info', foreground='#FFFF00')
        self.conversation_area.tag_config('loading', foreground='#888888')

        self.input_frame = tk.Frame(self.master, bg="#001a2a")
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.user_input_entry = tk.Entry(self.input_frame, bg="#002a3a", fg="#aaffff", font=("Consolas", 12), insertbackground="#FFFFFF")
        self.user_input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.user_input_entry.bind("<Return>", self.send_message)

        self.send_button = ttk.Button(self.input_frame, text="DIAL", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=(5, 0))

        self.memory_button = ttk.Button(self.input_frame, text="MEMORY CORE", command=self.launch_memory_visualizer)
        self.memory_button.pack(side=tk.LEFT, padx=(5, 0))

        self.display_message("SYSTEM: STARLITE hive mind and ArcNet online. Awaiting your command, Starpilot, for real.", 'info')

        self.check_ollama_status_thread = threading.Thread(target=self.check_ollama_status, daemon=True)
        self.check_ollama_status_thread.start()

    def send_message(self, event=None):
        user_input = self.user_input_entry.get()
        if not user_input:
            return

        self.display_message(f"STARPILOT: {user_input}", 'user')
        self.user_input_entry.delete(0, END)
        self.open_stargate()
        self.hive_mind.process_input(user_input)

    def display_message(self, message, tag, color=None, loading=False):
        self.conversation_area.configure(state='normal')

        if self.loading_message_id is not None and not loading:
            try:
                self.conversation_area.delete(self.loading_message_id, f"{self.loading_message_id} lineend")
                self.loading_message_id = None
            except tk.TclError:
                pass

        if loading:
            self.loading_message_id = self.conversation_area.index('end-1c')
            self.conversation_area.insert(END, message, ('loading',))
        else:
            if color:
                self.conversation_area.tag_config(tag, foreground=color)
            self.conversation_area.insert(END, f"{message}\n", (tag,))
            self.voice_interface.speak(message)

        self.conversation_area.see(END)
        self.conversation_area.configure(state='disabled')

    def open_stargate(self):
        self.stargate_event_horizon_width = 0
        self.animate_stargate_open_step()

    def animate_stargate_open_step(self):
        if self.stargate_event_horizon_width < 60:
            self.stargate_event_horizon_width += 3
            center = 100
            x1 = center - self.stargate_event_horizon_width
            y1 = center - self.stargate_event_horizon_width
            x2 = center + self.stargate_event_horizon_width
            y2 = center + self.stargate_event_horizon_width
            self.stargate_canvas.coords(self.stargate_event_horizon, x1, y1, x2, y2)
            self.stargate_canvas.itemconfig(self.stargate_event_horizon, outline="#00ffff", fill="#00aaff")
            self.master.after(50, self.animate_stargate_open_step)

    def close_stargate(self):
        self.stargate_event_horizon_width = 60
        self.animate_stargate_close_step()

    def animate_stargate_close_step(self):
        if self.stargate_event_horizon_width > 0:
            self.stargate_event_horizon_width -= 3
            center = 100
            x1 = center - self.stargate_event_horizon_width
            y1 = center - self.stargate_event_horizon_width
            x2 = center + self.stargate_event_horizon_width
            y2 = center + self.stargate_event_horizon_width
            self.stargate_canvas.coords(self.stargate_event_horizon, x1, y1, x2, y2)
            self.master.after(50, self.animate_stargate_close_step)
        else:
            self.stargate_canvas.itemconfig(self.stargate_event_horizon, outline="#000000", fill="#000000")

    def hide_loading_message(self):
        self.conversation_area.configure(state='normal')
        if self.loading_message_id is not None:
            try:
                self.conversation_area.delete(self.loading_message_id, f"{self.loading_message_id} lineend")
                self.loading_message_id = None
            except tk.TclError:
                pass
        self.conversation_area.configure(state='disabled')
        self.close_stargate()

    def set_input_enabled(self, enabled):
        state = 'normal' if enabled else 'disabled'
        self.user_input_entry.config(state=state)
        self.send_button.config(state=state)

    def update_agent_status(self, agent_name, response):
        status_text = f"{agent_name}: Responded"
        color = "#00ff00"
        self.master.after(0, lambda: self.agent_labels[agent_name].config(text=status_text, fg=color))
        self.master.after(0, lambda: self.display_message(f"Agent '{agent_name}' finished processing.", 'info', "#00ff00"))

    def update_hive_mind_stats(self):
        for name in self.agent_labels:
            self.master.after(0, lambda n=name: self.agent_labels[n].config(text=f"{n}: Ready", fg="#00ffff"))

    def check_ollama_status(self):
        while True:
            try:
                response = requests.get('http://localhost:11434', timeout=5)
                status = "Connected" if response.ok else "Disconnected"
            except requests.exceptions.RequestException:
                status = "Disconnected"

            if status != self.ollama_status_cache['status']:
                self.ollama_status_cache['status'] = status
                color = "#00ff00" if status == "Connected" else "#ff0000"
                self.master.after(0, lambda: self.display_message(f"Ollama Status: {status}", 'info', color))
            time.sleep(10)

    def launch_memory_visualizer(self):
        MemoryVisualizer(self.master, self.hive_mind.memory)
