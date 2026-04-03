"""
FocusFlow: The Gamified Study Engine — Tkinter GUI Edition
==========================================================
Computational Thinking Concepts:
  - Decomposition : Each feature is its own function
  - Abstraction   : UI separated from data/logic
  - Algorithm     : XP, level-up, boss-battle logic
  - Data Struct.  : Dictionary holds all profile state
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import os

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
SAVE_FILE     = "focus_save.txt"
XP_PER_TASK   = 20
XP_PER_LEVEL  = 100
BOSS_EVERY    = 3       # Boss appears every N completed tasks
BOSS_BONUS_XP = 50

ACHIEVEMENTS = {
    5:  "📚 Bookworm    — 5 tasks done!",
    10: "🔥 On Fire     — 10 tasks done!",
    25: "⚡ Study Beast  — 25 tasks done!",
    50: "🏆 Legend       — 50 tasks done!",
}

# ─────────────────────────────────────────────
# DATA  (Decomposition: data layer)
# ─────────────────────────────────────────────

def default_profile(name: str) -> dict:
    """Create a fresh character dictionary — Abstraction over raw dict."""
    return {
        "name"         : name,
        "level"        : 1,
        "xp"           : 0,
        "tasks_done"   : 0,
        "achievements" : [],
    }

def save_data(profile: dict) -> None:
    """Algorithm: Serialise profile to focus_save.txt as key=value lines."""
    with open(SAVE_FILE, "w") as f:
        f.write(f"name={profile['name']}\n")
        f.write(f"level={profile['level']}\n")
        f.write(f"xp={profile['xp']}\n")
        f.write(f"tasks_done={profile['tasks_done']}\n")
        achievements_str = "|".join(profile["achievements"])
        f.write(f"achievements={achievements_str}\n")

def load_data() -> dict | None:
    """Algorithm: Parse focus_save.txt back into a profile dictionary."""
    if not os.path.exists(SAVE_FILE):
        return None
    profile = {}
    with open(SAVE_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key in ("level", "tasks_done"):
                profile[key] = int(value)
            elif key == "xp":
                profile[key] = int(value)
            elif key == "achievements":
                profile[key] = [a for a in value.split("|") if a]
            else:
                profile[key] = value
    # Guard: ensure all expected keys exist
    for k, default in [("level",1),("xp",0),("tasks_done",0),("achievements",[])]:
        profile.setdefault(k, default)
    return profile

# ─────────────────────────────────────────────
# BOSS BATTLE  (Decomposition: isolated feature)
# ─────────────────────────────────────────────

def run_boss_battle(parent) -> int:
    """
    Distraction Boss mini-game.
    Returns XP bonus earned (50 on win, 0 on loss).
    Uses random module for math challenge generation.
    """
    a  = random.randint(10, 50)
    b  = random.randint(5,  30)
    op = random.choice(["+", "-", "*"])
    answer = eval(f"{a}{op}{b}")   # safe: operands are ints, op is controlled

    messagebox.showwarning(
        "⚠️  DISTRACTION BOSS APPEARED!",
        f"A wild Distraction Monster blocks your path!\n\n"
        f"Solve this to defeat it:\n\n"
        f"   {a}  {op}  {b}  = ?\n\n"
        "Click OK then type your answer.",
        parent=parent
    )

    for attempt in range(1, 4):          # 3 attempts
        raw = simpledialog.askstring(
            "Boss Battle",
            f"Attempt {attempt}/3 — What is  {a} {op} {b}?",
            parent=parent
        )
        if raw is None:                  # user cancelled
            break
        raw = raw.strip()
        # Input validation — handle negatives
        if not raw.lstrip("-").lstrip().isdigit():
            messagebox.showerror("Invalid", "Please enter a number!", parent=parent)
            continue
        if int(raw) == answer:
            messagebox.showinfo(
                "⚔️  BOSS DEFEATED!",
                f"Correct! The answer was {answer}.\n"
                f"You earn +{BOSS_BONUS_XP} Bonus XP! 🎉",
                parent=parent
            )
            return BOSS_BONUS_XP

    messagebox.showerror(
        "💀 Boss Won...",
        f"The correct answer was {answer}.\n"
        "No bonus XP this time. Stay focused! 💪",
        parent=parent
    )
    return 0

# ─────────────────────────────────────────────
# MAIN GUI CLASS  (Abstraction: UI layer)
# ─────────────────────────────────────────────

class FocusFlowApp(tk.Tk):
    """Main application window — all widgets and event handlers live here."""

    # ── Initialisation ──────────────────────────────────────────────────────
    def __init__(self):
        super().__init__()
        self.title("🎮  FocusFlow — Gamified Study Engine")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")

        # Load existing save or prompt for name
        saved = load_data()
        if saved:
            self.profile = saved
            restored = True
        else:
            name = self._ask_name()
            self.profile = default_profile(name)
            restored = False

        self._build_ui()
        self._refresh_ui()

        if restored:
            messagebox.showinfo(
                "Welcome Back!",
                f"Progress restored for {self.profile['name']}!\n"
                f"Level {self.profile['level']}  •  "
                f"{self.profile['xp']} XP  •  "
                f"{self.profile['tasks_done']} tasks done 🚀",
                parent=self
            )

    def _ask_name(self) -> str:
        """Prompt for player name with fallback."""
        name = simpledialog.askstring(
            "Welcome to FocusFlow!",
            "Enter your name to begin your journey:",
            parent=self
        )
        return (name.strip() if name and name.strip() else "Student")

    # ── UI Construction ──────────────────────────────────────────────────────
    def _build_ui(self):
        """Decomposition: every section of the UI is built by a helper call."""
        PAD = {"padx": 20, "pady": 8}

        # ── Header ──────────────────────────────────────────────────────────
        header = tk.Frame(self, bg="#313244", pady=12)
        header.pack(fill="x")
        tk.Label(
            header, text="🎮  FocusFlow", font=("Helvetica", 22, "bold"),
            fg="#cba6f7", bg="#313244"
        ).pack()
        tk.Label(
            header, text="Gamified Study Engine",
            font=("Helvetica", 10), fg="#a6adc8", bg="#313244"
        ).pack()

        # ── Stats card ──────────────────────────────────────────────────────
        card = tk.Frame(self, bg="#313244", padx=20, pady=14, relief="flat")
        card.pack(fill="x", **PAD)

        self.lbl_name  = tk.Label(card, font=("Helvetica", 13, "bold"),
                                  fg="#cdd6f4", bg="#313244")
        self.lbl_level = tk.Label(card, font=("Helvetica", 11),
                                  fg="#89b4fa", bg="#313244")
        self.lbl_xp    = tk.Label(card, font=("Helvetica", 11),
                                  fg="#a6e3a1", bg="#313244")
        self.lbl_tasks = tk.Label(card, font=("Helvetica", 10),
                                  fg="#f38ba8", bg="#313244")

        self.lbl_name .pack(anchor="w")
        self.lbl_level.pack(anchor="w")
        self.lbl_xp   .pack(anchor="w")
        self.lbl_tasks.pack(anchor="w")

        # ── XP Progress bar ─────────────────────────────────────────────────
        pb_frame = tk.Frame(self, bg="#1e1e2e")
        pb_frame.pack(fill="x", padx=20, pady=4)

        tk.Label(pb_frame, text="XP Progress", font=("Helvetica", 9),
                 fg="#a6adc8", bg="#1e1e2e").pack(anchor="w")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "XP.Horizontal.TProgressbar",
            troughcolor="#313244",
            background="#cba6f7",
            thickness=22,
            bordercolor="#1e1e2e",
        )
        self.progress = ttk.Progressbar(
            pb_frame, style="XP.Horizontal.TProgressbar",
            orient="horizontal", length=360,
            mode="determinate", maximum=XP_PER_LEVEL
        )
        self.progress.pack(fill="x", pady=4)

        self.lbl_progress = tk.Label(pb_frame, font=("Helvetica", 9),
                                     fg="#a6adc8", bg="#1e1e2e")
        self.lbl_progress.pack(anchor="e")

        # ── Action button ────────────────────────────────────────────────────
        self.btn_task = tk.Button(
            self,
            text="✅  Complete Study Session  (+20 XP)",
            font=("Helvetica", 12, "bold"),
            bg="#cba6f7", fg="#1e1e2e",
            activebackground="#b4befe",
            relief="flat", cursor="hand2", pady=10,
            command=self._on_complete_task
        )
        self.btn_task.pack(fill="x", padx=20, pady=10)

        # ── Achievements panel ───────────────────────────────────────────────
        ach_outer = tk.Frame(self, bg="#1e1e2e")
        ach_outer.pack(fill="x", padx=20, pady=(0, 6))
        tk.Label(ach_outer, text="🏆  Achievements",
                 font=("Helvetica", 10, "bold"),
                 fg="#f9e2af", bg="#1e1e2e").pack(anchor="w")

        self.lbl_achievements = tk.Label(
            ach_outer, text="", font=("Helvetica", 9),
            fg="#a6adc8", bg="#1e1e2e",
            justify="left", wraplength=340
        )
        self.lbl_achievements.pack(anchor="w")

        # ── Footer buttons ───────────────────────────────────────────────────
        foot = tk.Frame(self, bg="#1e1e2e")
        foot.pack(fill="x", padx=20, pady=(4, 16))

        tk.Button(
            foot, text="💾  Save", font=("Helvetica", 10),
            bg="#313244", fg="#a6e3a1",
            activebackground="#45475a",
            relief="flat", cursor="hand2", padx=12, pady=6,
            command=self._on_save
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            foot, text="🔄  Reset", font=("Helvetica", 10),
            bg="#313244", fg="#f38ba8",
            activebackground="#45475a",
            relief="flat", cursor="hand2", padx=12, pady=6,
            command=self._on_reset
        ).pack(side="left")

        tk.Button(
            foot, text="❌  Exit", font=("Helvetica", 10),
            bg="#313244", fg="#cdd6f4",
            activebackground="#45475a",
            relief="flat", cursor="hand2", padx=12, pady=6,
            command=self._on_exit
        ).pack(side="right")

    # ── UI Refresh  (Abstraction: one call syncs all labels) ─────────────────
    def _refresh_ui(self):
        """Sync every widget to the current profile state."""
        p = self.profile
        xp_in_level = p["xp"] % XP_PER_LEVEL

        self.lbl_name .config(text=f"👤  {p['name']}")
        self.lbl_level.config(text=f"⭐  Level  {p['level']}")
        self.lbl_xp   .config(text=f"✨  Total XP: {p['xp']}")
        self.lbl_tasks.config(text=f"📋  Tasks Completed: {p['tasks_done']}")

        self.progress["value"]  = xp_in_level
        self.lbl_progress.config(
            text=f"{xp_in_level} / {XP_PER_LEVEL} XP  to next level"
        )

        if p["achievements"]:
            self.lbl_achievements.config(
                text="\n".join(p["achievements"])
            )
        else:
            self.lbl_achievements.config(text="None yet — keep studying!")

    # ── Core Logic (Decomposition: each action is its own method) ────────────
    def _on_complete_task(self):
        """Complete a study session: award XP, check level-up, maybe boss."""
        p = self.profile

        # Award XP
        p["xp"]         += XP_PER_TASK
        p["tasks_done"] += 1

        # Check achievements (Pattern Recognition)
        self._check_achievements()

        # Level-up loop (handles multiple level-ups at once)
        levelled_up = False
        while p["xp"] >= p["level"] * XP_PER_LEVEL:
            p["level"] += 1
            levelled_up = True

        if levelled_up:
            messagebox.showinfo(
                "🎉  LEVEL UP!",
                f"Amazing work, {p['name']}!\n\n"
                f"You reached  ⭐ Level {p['level']} ⭐\n\n"
                "Keep crushing those study sessions! 🚀",
                parent=self
            )

        # Boss battle every BOSS_EVERY tasks
        if p["tasks_done"] % BOSS_EVERY == 0:
            bonus = run_boss_battle(self)
            if bonus:
                p["xp"] += bonus
                # Re-check level-up after bonus XP
                while p["xp"] >= p["level"] * XP_PER_LEVEL:
                    p["level"] += 1
                    messagebox.showinfo(
                        "🎉  LEVEL UP!",
                        f"Bonus XP pushed you to Level {p['level']}! 🔥",
                        parent=self
                    )
        else:
            messagebox.showinfo(
                "✅  Session Complete!",
                f"+{XP_PER_TASK} XP earned!\n\n"
                f"Total XP: {p['xp']}  •  Level: {p['level']}\n\n"
                f"Tasks done: {p['tasks_done']}",
                parent=self
            )

        save_data(p)
        self._refresh_ui()

    def _check_achievements(self):
        """Pattern Recognition: unlock badges at task milestones."""
        p    = self.profile
        done = p["tasks_done"]
        if done in ACHIEVEMENTS:
            badge = ACHIEVEMENTS[done]
            if badge not in p["achievements"]:
                p["achievements"].append(badge)
                messagebox.showinfo(
                    "🏆  Achievement Unlocked!",
                    badge, parent=self
                )

    def _on_save(self):
        save_data(self.profile)
        messagebox.showinfo("💾  Saved",
                            "Your progress has been saved!", parent=self)

    def _on_reset(self):
        if messagebox.askyesno(
            "🔄  Reset",
            "This will erase ALL progress.\nAre you sure?",
            parent=self
        ):
            name = self._ask_name()
            self.profile = default_profile(name)
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            self._refresh_ui()
            messagebox.showinfo("Reset Complete",
                                f"New journey started for {name}! 🌟",
                                parent=self)

    def _on_exit(self):
        save_data(self.profile)
        self.destroy()


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = FocusFlowApp()
    app.mainloop()
