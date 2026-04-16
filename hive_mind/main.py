import tkinter as tk
from .logic import HiveMind
from .gui import STARLITEGUI

def main():
    root = tk.Tk()
    hive_mind = HiveMind(num_agents=3)
    app = STARLITEGUI(root, hive_mind)
    root.mainloop()

if __name__ == "__main__":
    main()
