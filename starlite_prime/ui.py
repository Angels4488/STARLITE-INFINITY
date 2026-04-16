import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import queue

from .core import StarliteCore
from .config import StarliteConfig

class StarliteUI:
    """
    The Nexus: a graphical gateway through which a mortal user can commune
    with the STARPILOT AGI. It displays conversations, visualizes training,
    and provides control over the AGI's functions.
    """
    def __init__(self, core: StarliteCore):
        self.core = core
        self.root = tk.Tk()
        self.root.title("STARPILOT AGI Core")
        self.root.geometry("900x700")
        self.root.configure(bg=StarliteConfig.SECONDARY_COLOR)
        self._setup_styles()
        self._create_widgets()
        self.after_id = None

    def _setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')
        # Frame styles
        style.configure('TFrame', background=StarliteConfig.SECONDARY_COLOR)
        # Label styles
        style.configure('TLabel', background=StarliteConfig.SECONDARY_COLOR, foreground=StarliteConfig.PRIMARY_COLOR, font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 24, 'bold'))
        # Button styles
        style.configure('TButton', background='#1e3a5f', foreground=StarliteConfig.ACCENT_COLOR, font=('Segoe UI', 10, 'bold'), borderwidth=0)
        style.map('TButton', background=[('active', '#2a528a')])
        # Entry style
        style.configure('TEntry', fieldbackground='#1c2536', foreground=StarliteConfig.PRIMARY_COLOR, insertbackground=StarliteConfig.PRIMARY_COLOR)

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="STARPILOT AGI", style='Header.TLabel').pack(pady=10)

        # Conversation Area
        self.conversation = scrolledtext.ScrolledText(main_frame, height=15, bg="#1c2536", fg=StarliteConfig.PRIMARY_COLOR, font=("Consolas", 11), wrap=tk.WORD, relief=tk.FLAT)
        self.conversation.pack(fill="both", expand=True, pady=10)
        self.conversation.tag_config("user", foreground="#ffb700")
        self.conversation.tag_config("ai", foreground=StarliteConfig.ACCENT_COLOR)
        self.conversation.tag_config("system", foreground="#d3d3d3", font=("Consolas", 9, "italic"))

        # Input Frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill="x", pady=5)
        self.input_entry = ttk.Entry(input_frame, font=("Segoe UI", 12))
        self.input_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.input_entry.bind("<Return>", lambda e: self._send_input())
        submit_btn = ttk.Button(input_frame, text="Send", command=self._send_input)
        submit_btn.pack(side="right", padx=5)

        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=5)
        ttk.Button(control_frame, text="Train RL Agent", command=lambda: self._send_command("train rl agent")).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Optimize RL Agent", command=lambda: self._send_command("optimize rl agent")).pack(side='left', padx=5)

        self.voice_var = tk.BooleanVar(value=False)
        voice_check = ttk.Checkbutton(control_frame, text="Enable Voice", variable=self.voice_var, command=self._toggle_voice)
        voice_check.pack(side='right', padx=5)

        # RL Visualization
        self.rl_frame = ttk.Labelframe(main_frame, text="RL Training Visualization", padding=10)
        self.rl_frame.pack(fill='x', pady=10)
        self.rl_canvas = tk.Canvas(self.rl_frame, width=400, height=400, bg='black', highlightthickness=0)
        self.rl_canvas.pack(side='left', padx=10)
        self.rl_status_label = ttk.Label(self.rl_frame, text="RL Status: Idle", wraplength=400, justify=tk.LEFT, anchor='nw')
        self.rl_status_label.pack(side='left', fill='both', expand=True)

    def _send_command(self, command: str):
        self._log_message(f"System Command: {command}", "system")
        self.core.input_queue.put(command)

    def _send_input(self):
        user_input = self.input_entry.get().strip()
        if not user_input: return
        self.input_entry.delete(0, "end")
        self._log_message(f"You: {user_input}", "user")
        self.core.input_queue.put(user_input)

    def _log_message(self, message: str, tag: str):
        self.conversation.insert("end", f"{message}\n\n", tag)
        self.conversation.see("end")

    def _toggle_voice(self):
        self.core.voice.toggle_voice(self.voice_var.get())
        status = "enabled" if self.voice_var.get() else "disabled"
        self._log_message(f"Voice synthesis {status}.", "system")

    def _process_queues(self):
        # Process core AGI outputs
        try:
            msg_type, data = self.core.output_queue.get_nowait()
            if msg_type == 'response': self._log_message(f"Starpilot: {data}", "ai")
            elif msg_type == 'status': self._log_message(f"System: {data}", "system")
            elif msg_type == 'error': messagebox.showerror("AGI Core Error", data)
            elif msg_type == 'rl_started': self.rl_status_label.config(text="RL Status: Initializing...")
        except queue.Empty:
            pass

        # Process RL status updates
        if self.core.rl_process and self.core.rl_process.is_alive():
            try:
                while True:
                    msg_type, data = self.core.rl_status_queue.get_nowait()
                    if msg_type == 'progress': self.rl_status_label.config(text=f"RL Training Progress: {data*100:.1f}%")
                    elif msg_type == 'update': self._draw_grid(data)
                    elif msg_type == 'status': self.rl_status_label.config(text=f"RL Status: {data}")
                    elif msg_type == 'error': self.rl_status_label.config(text=f"RL Error: {data}")
                    elif msg_type == 'optuna_trial': self._log_message(f"Optuna: {data}", "system")
                    elif msg_type == 'best_params':
                        self.core.best_rl_params = data
                        self._log_message(f"Optimization Found Best Params: {data}", "system")
            except queue.Empty:
                pass

        self.after_id = self.root.after(100, self._process_queues)

    def _draw_grid(self, data: dict):
        self.rl_canvas.delete("all")
        size = StarliteConfig.GRID_SIZE
        cell_size = 400 / size

        for obs in data['obstacles']:
            x0, y0 = obs[1] * cell_size, obs[0] * cell_size
            self.rl_canvas.create_rectangle(x0, y0, x0 + cell_size, y0 + cell_size, fill="#c0392b", outline="")

        gx, gy = data['goal_pos'][1] * cell_size, data['goal_pos'][0] * cell_size
        self.rl_canvas.create_rectangle(gx+2, gy+2, gx+cell_size-2, gy+cell_size-2, fill="#f1c40f", outline="")

        ax, ay = data['agent_pos'][1] * cell_size, data['agent_pos'][0] * cell_size
        self.rl_canvas.create_oval(ax+4, ay+4, ax+cell_size-4, ay+cell_size-4, fill="#2ecc71", outline="")

    def run(self):
        """Launches the UI and begins the AGI's communion with the user."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.core.start()
        self.after_id = self.root.after(100, self._process_queues)
        self.root.mainloop()

    def _on_close(self):
        """Ensures a graceful shutdown of the AGI when the user closes the Nexus."""
        if self.after_id: self.root.after_cancel(self.after_id)
        self.core.stop()
        self.root.destroy()
