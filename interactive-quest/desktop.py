"""Small draggable desktop shell for the existing game engine."""
import ctypes
import queue
import sys
import time
import tkinter as tk
from tkinter import messagebox

from engine import Game
from global_input import GlobalInput


class DesktopPanel:
    WIDTH = 390
    HEIGHT = 240

    def __init__(self, root):
        self.root = root
        self.events = queue.SimpleQueue()
        self.listener = GlobalInput(self.events)
        self.game = Game()
        self.closed = False
        self.drag_offset = (0, 0)
        root.title("Interactive Quest")
        root.configure(bg="#38383e")
        root.resizable(False, False)
        root.attributes("-topmost", True)
        root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{max(0, root.winfo_screenwidth()-self.WIDTH-40)}+80")
        root.protocol("WM_DELETE_WINDOW", self.close)

        header = tk.Frame(root, bg="#29292e", height=34)
        header.pack(fill="x", padx=1, pady=(1, 0))
        title = tk.Label(header, text="INTERACTIVE QUEST   /   drag to move", bg="#29292e",
                         fg="#c6c6ce", font=("Segoe UI", 9))
        title.pack(side="left", padx=10, pady=8)
        for widget in (header, title):
            widget.bind("<ButtonPress-1>", self.begin_drag)
            widget.bind("<B1-Motion>", self.drag)
        tk.Button(header, text="×", command=self.close, bg="#29292e", fg="#ccccd4",
                  activebackground="#713535", activeforeground="white", bd=0,
                  font=("Segoe UI", 12), width=3).pack(side="right")
        body = tk.Frame(root, bg="#17171b")
        body.pack(fill="both", expand=True, padx=1, pady=(0, 1))
        row = tk.Frame(body, bg="#17171b")
        row.pack(fill="x", padx=12, pady=(9, 0))
        self.mode = tk.Label(row, bg="#17171b", fg="#c5baa1", font=("Segoe UI", 9, "bold"))
        self.mode.pack(side="left")
        tk.Button(row, text="Auto", command=self.auto, bg="#35353c", fg="#eeeeee",
                  activebackground="#45454e", activeforeground="white", bd=0,
                  padx=12, font=("Segoe UI", 9)).pack(side="right")
        self.canvas = tk.Canvas(body, width=366, height=86, bg="#17171b", highlightthickness=0)
        self.canvas.pack(padx=10, pady=(5, 0))
        self.canvas.create_line(5, 70, 360, 70, fill="#414148")
        self.hero = self.canvas.create_rectangle(52, 27, 76, 69, fill="#aaaaaf", outline="")
        self.canvas.create_text(64, 14, text="YOU", fill="#92929a", font=("Segoe UI", 8))
        self.enemy = self.canvas.create_rectangle(284, 33, 312, 69, fill="#6b5050", outline="")
        self.enemy_label = self.canvas.create_text(298, 14, text="ENEMY", fill="#92929a", font=("Segoe UI", 8))
        self.scene_text = self.canvas.create_text(183, 47, text="", fill="#ceced5", font=("Segoe UI", 9))
        self.stats = tk.Label(body, bg="#17171b", fg="#d2d2da", font=("Segoe UI", 10))
        self.stats.pack(pady=(0, 3))
        self.note = tk.Label(body, bg="#17171b", fg="#8e8e99", font=("Segoe UI", 8))
        self.note.pack()
        self.last_actions = 0
        self.flash_until = 0
        try:
            self.listener.start()
        except Exception:
            self.listener.stop()
            raise
        root.after(16, self.update)

    def begin_drag(self, event):
        self.drag_offset = (event.x_root - self.root.winfo_x(), event.y_root - self.root.winfo_y())

    def drag(self, event):
        x = event.x_root - self.drag_offset[0]
        y = event.y_root - self.drag_offset[1]
        self.root.geometry(f"{x:+d}{y:+d}")

    def auto(self):
        # Defer until the hook event for the button click has been processed.
        self.events.put(("auto", time.monotonic()))

    def update(self):
        if self.closed:
            return
        for _ in range(10000):
            try:
                kind, now = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == "input":
                self.game.input_action(now)
            elif kind == "auto":
                self.game.enable_auto(now)
        now = time.monotonic()
        self.game.tick(now)
        game = self.game
        if game.actions != self.last_actions:
            self.flash_until = now + 0.10
            self.last_actions = game.actions
        self.canvas.itemconfigure(self.hero, fill="#eeeeef" if now < self.flash_until else "#aaaaaf")
        market = game.location == "market"
        self.canvas.itemconfigure(self.enemy, state="hidden" if market else "normal")
        self.canvas.itemconfigure(self.enemy_label, text="MARKET" if market else "ENEMY")
        self.canvas.itemconfigure(self.scene_text, text="Selling loot next" if market else f"HP {game.health}/{game.rules.enemy_health}")
        self.mode.configure(text=f"{game.mode.upper()}  ·  {game.location.upper()}")
        self.stats.configure(text=f"XP {game.xp}     Gold {game.gold}     Loot {game.loot}     Kills {game.kills}")
        remaining = max(0, game.rules.idle_seconds - (now - game.last_input)) if game.last_input is not None else 0
        self.note.configure(text=f"Auto in {remaining:.0f}s  ·  Actions {game.actions}" if game.mode == "active"
                            else f"Auto running  ·  Type or click anywhere  ·  Actions {game.actions}")
        self.root.after(16, self.update)

    def close(self):
        if not self.closed:
            self.closed = True
            self.listener.stop()
            self.root.destroy()


def main():
    if sys.platform != "win32":
        raise SystemExit("This desktop prototype requires Windows.")
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (OSError, AttributeError):
        pass
    root = tk.Tk()
    root.withdraw()
    try:
        panel = DesktopPanel(root)
    except Exception as exc:
        messagebox.showerror("Interactive Quest could not start", str(exc), parent=root)
        root.destroy()
        return
    root.deiconify()
    try:
        root.mainloop()
    finally:
        panel.close()


if __name__ == "__main__":
    main()
