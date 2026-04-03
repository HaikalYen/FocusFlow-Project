# ==============================================================
#  FocusFlow: The Gamified Study Engine
#  A single-file Python terminal app for a Computational Thinking project.
#
#  Computational Thinking Concepts Used:
#  ► DECOMPOSITION  : The problem is broken into smaller functions,
#                     each handling one responsibility.
#  ► ABSTRACTION    : Complex logic (XP math, boss battles, file I/O)
#                     is hidden inside functions so the main menu
#                     stays simple and readable.
#  ► PATTERN REC.   : Level-up and achievement checks follow a
#                     repeating pattern triggered after every task.
#  ► ALGORITHMS     : Step-by-step logic for XP gain, boss battles,
#                     saving/loading data.
# ==============================================================

import random   # For generating random math problems in the Boss Battle
import os       # For checking if the save file exists

# ── Constants ─────────────────────────────────────────────────
SAVE_FILE       = "focus_save.txt"  # File used for saving/loading progress
XP_PER_MINUTE   = 5                 # XP earned per minute of study time
XP_TO_LEVEL     = 100               # XP required to reach the next level
BOSS_TASK_LIMIT = 3                 # A boss appears every N completed tasks
BOSS_BONUS_XP   = 50                # Bonus XP for defeating the boss
SEPARATOR       = "=" * 52          # Reusable ASCII border line


# ══════════════════════════════════════════════════════════════
#  SECTION 1 — PROFILE MANAGEMENT  (Abstraction)
#  These functions hide all the complexity of creating and
#  accessing the user's data dictionary.
# ══════════════════════════════════════════════════════════════

def create_profile(name: str) -> dict:
    """
    ABSTRACTION — Builds and returns the core user profile dictionary.
    All other functions receive this dict and interact with it.
    """
    return {
        "name":           name,
        "level":          1,
        "xp":             0,
        "tasks_done":     0,   # Counts tasks since last boss encounter
        "total_tasks":    0,   # Lifetime task count
        "achievements":   [],  # List of unlocked achievement strings
    }


def check_achievements(profile: dict) -> None:
    """
    PATTERN RECOGNITION — Checks for repeating milestone patterns
    and unlocks the matching achievement badge if not already earned.
    """
    # ── Achievement definitions: (condition_value, badge_string)
    milestones = [
        (profile["total_tasks"] >= 1,    "🏅 First Step   — Completed your 1st task!"),
        (profile["total_tasks"] >= 5,    "🥉 Getting Warm  — Completed 5 tasks!"),
        (profile["total_tasks"] >= 10,   "🥈 On a Roll     — Completed 10 tasks!"),
        (profile["total_tasks"] >= 25,   "🥇 Study Machine — Completed 25 tasks!"),
        (profile["level"]       >= 3,    "⭐ Rising Star   — Reached Level 3!"),
        (profile["level"]       >= 5,    "🌟 Scholar       — Reached Level 5!"),
        (profile["level"]       >= 10,   "💎 Legend        — Reached Level 10!"),
    ]

    for condition, badge in milestones:
        if condition and badge not in profile["achievements"]:
            profile["achievements"].append(badge)
            print(f"\n  🎊  ACHIEVEMENT UNLOCKED: {badge}")


# ══════════════════════════════════════════════════════════════
#  SECTION 2 — DISPLAY  (Abstraction)
#  Hides all formatting logic so the main loop stays clean.
# ══════════════════════════════════════════════════════════════

def show_stats(profile: dict) -> None:
    """
    ABSTRACTION — Displays the user's current stats in a formatted
    terminal card. The main loop just calls show_stats(profile).
    """
    xp_needed      = XP_TO_LEVEL - profile["xp"]
    bar_filled     = int((profile["xp"] / XP_TO_LEVEL) * 24)
    xp_bar         = "█" * bar_filled + "░" * (24 - bar_filled)

    print(f"\n  {SEPARATOR}")
    print(f"  {'📊  FOCUSFLOW — STATS':^52}")
    print(f"  {SEPARATOR}")
    print(f"  👤  Name         : {profile['name']}")
    print(f"  ⭐  Level        : {profile['level']}")
    print(f"  ✨  XP           : {profile['xp']} / {XP_TO_LEVEL}  "
          f"({xp_needed} XP to next level)")
    print(f"  📈  Progress     : [{xp_bar}]")
    print(f"  📚  Total Tasks  : {profile['total_tasks']}")
    print()

    if profile["achievements"]:
        print(f"  🏆  Achievements ({len(profile['achievements'])}):")
        for badge in profile["achievements"]:
            print(f"      {badge}")
    else:
        print("  🏆  Achievements : None yet — keep studying!")

    print(f"  {SEPARATOR}\n")


# ══════════════════════════════════════════════════════════════
#  SECTION 3 — TASK MANAGEMENT  (Decomposition)
#  The task workflow is split into two functions:
#  add_task()  → collects input from the user
#  complete_task() → processes XP and level logic
# ══════════════════════════════════════════════════════════════

def add_task() -> tuple[str, int]:
    """
    DECOMPOSITION — Handles ONLY the task input step.
    Validates that duration is a positive integer.
    Returns (task_name, duration_in_minutes).
    """
    print(f"\n  {SEPARATOR}")
    print(f"  {'📝  ADD A NEW STUDY TASK':^52}")
    print(f"  {SEPARATOR}")

    task_name = input("  Task name (e.g. 'Read Chapter 4'): ").strip()
    if not task_name:
        task_name = "Study Session"

    # ── Input Validation Loop ─────────────────────────────────
    while True:
        raw = input("  Duration in minutes          : ").strip()
        if raw.isdigit() and int(raw) > 0:
            duration = int(raw)
            break
        print("  ⚠️   Please enter a whole positive number (e.g. 30).")

    print(f"  {SEPARATOR}\n")
    return task_name, duration


def complete_task(profile: dict, task_name: str, duration: int) -> None:
    """
    DECOMPOSITION — Handles ONLY the XP/level logic after a task is added.
    ABSTRACTION   — Callers don't need to know HOW XP or levels work.

    Awards XP based on duration, checks for level-up(s), updates counters,
    checks for achievements, then checks if a boss battle should trigger.
    """
    xp_earned = duration * XP_PER_MINUTE

    profile["xp"]           += xp_earned
    profile["tasks_done"]   += 1
    profile["total_tasks"]  += 1

    print(f"\n  ✅  '{task_name}' logged!  You earned +{xp_earned} XP "
          f"({duration} min × {XP_PER_MINUTE} XP/min)")

    # ── Level-Up Check (loop handles multiple level-ups at once) ──
    while profile["xp"] >= XP_TO_LEVEL:
        profile["xp"]    -= XP_TO_LEVEL
        profile["level"] += 1
        print(f"\n  {'*' * 52}")
        print(f"  🎉  LEVEL UP!  {profile['name']} is now LEVEL {profile['level']}! 🎉")
        print(f"  {'*' * 52}")

    # ── Achievement Check ─────────────────────────────────────
    check_achievements(profile)

    # ── Boss Battle Check ─────────────────────────────────────
    if profile["tasks_done"] >= BOSS_TASK_LIMIT:
        profile["tasks_done"] = 0          # Reset counter
        distraction_boss(profile)


# ══════════════════════════════════════════════════════════════
#  SECTION 4 — THE BOSS BATTLE  (Decomposition + Random Module)
#  Every 3 completed tasks, a Distraction Monster appears.
#  The user must solve a random math problem to defeat it.
# ══════════════════════════════════════════════════════════════

def distraction_boss(profile: dict) -> None:
    """
    DECOMPOSITION — An isolated mini-game function.
    Uses the 'random' module to generate a math challenge.
    Gives 3 attempts before the boss wins.
    """
    print(f"\n  {'!' * 52}")
    print(f"  ⚔️   A DISTRACTION MONSTER HAS APPEARED! ⚔️")
    print(f"  {'!' * 52}")
    print("  The monster is trying to pull you off-task.")
    print(f"  Defeat it by solving this math challenge to earn +{BOSS_BONUS_XP} Bonus XP!\n")

    # ── Generate a random math problem ────────────────────────
    a, b      = random.randint(10, 50), random.randint(10, 50)
    operator  = random.choice(["+", "-", "*"])

    if operator == "+":
        answer = a + b
    elif operator == "-":
        answer = a - b
    else:
        answer = a * b

    print(f"  ❓  What is  {a} {operator} {b}  ?")
    print()

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        # ── Input Validation ───────────────────────────────────
        raw = input(f"  Your answer (Attempt {attempt}/{max_attempts}): ").strip()

        if not raw.lstrip("-").isdigit():
            print("  ⚠️   Numbers only — try again.\n")
            continue

        if int(raw) == answer:
            profile["xp"] += BOSS_BONUS_XP
            print(f"\n  🏆  CORRECT!  Monster defeated!  +{BOSS_BONUS_XP} Bonus XP!")

            # ── Check for level-up from bonus XP ──────────────
            while profile["xp"] >= XP_TO_LEVEL:
                profile["xp"]    -= XP_TO_LEVEL
                profile["level"] += 1
                print(f"  🎉  LEVEL UP from Boss Bonus!  Now Level {profile['level']}!")

            print(f"  {'!' * 52}\n")
            return  # Boss defeated — exit function

        else:
            remaining = max_attempts - attempt
            if remaining > 0:
                print(f"  ❌  Wrong!  {remaining} attempt(s) left.\n")
            else:
                print(f"\n  💀  The Distraction Monster wins this round...")
                print(f"      The correct answer was {answer}.")
                print(f"      Stay focused next time, {profile['name']}!")
                print(f"  {'!' * 52}\n")


# ══════════════════════════════════════════════════════════════
#  SECTION 5 — FILE I/O  (Decomposition)
#  Save/load are completely separate from all other logic.
#  They write and read a plain-text file named focus_save.txt.
# ══════════════════════════════════════════════════════════════

def save_data(profile: dict) -> None:
    """
    DECOMPOSITION — Handles ONLY the write-to-file step.
    Saves each profile field on its own line for easy parsing.
    """
    try:
        with open(SAVE_FILE, "w") as f:
            f.write(f"name={profile['name']}\n")
            f.write(f"level={profile['level']}\n")
            f.write(f"xp={profile['xp']}\n")
            f.write(f"tasks_done={profile['tasks_done']}\n")
            f.write(f"total_tasks={profile['total_tasks']}\n")

            # Achievements are joined with a pipe "|" so they fit on one line
            achievements_str = "|".join(profile["achievements"])
            f.write(f"achievements={achievements_str}\n")

        print(f"\n  💾  Progress saved to '{SAVE_FILE}'  ✔")

    except IOError as e:
        print(f"\n  ⚠️   Could not save file: {e}")


def load_data() -> dict | None:
    """
    DECOMPOSITION — Handles ONLY the read-from-file step.
    Returns a fully restored profile dict, or None if no save exists.
    """
    if not os.path.exists(SAVE_FILE):
        return None     # No save file found — signal caller to create a new profile

    try:
        profile = {}
        with open(SAVE_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")

                # ── Restore each field with its correct data type ──
                if key == "name":
                    profile["name"] = value
                elif key == "level":
                    profile["level"] = int(value)
                elif key == "xp":
                    profile["xp"] = int(value)
                elif key == "tasks_done":
                    profile["tasks_done"] = int(value)
                elif key == "total_tasks":
                    profile["total_tasks"] = int(value)
                elif key == "achievements":
                    profile["achievements"] = value.split("|") if value else []

        # Guard: ensure all expected keys exist (handles old/corrupt saves)
        required_keys = ["name", "level", "xp", "tasks_done", "total_tasks", "achievements"]
        if not all(k in profile for k in required_keys):
            print("  ⚠️   Save file is incomplete. Starting fresh.")
            return None

        return profile

    except (IOError, ValueError) as e:
        print(f"\n  ⚠️   Could not load save file: {e}  Starting fresh.")
        return None


# ══════════════════════════════════════════════════════════════
#  SECTION 6 — MAIN MENU LOOP  (Core Algorithm + Decomposition)
#  The main() function is the entry point and the glue layer.
#  It calls the other functions but contains NO complex logic itself.
# ══════════════════════════════════════════════════════════════

def main():
    """
    ALGORITHM — Controls the program's main flow:
    1. Display welcome screen
    2. Load save or create new profile
    3. Loop on main menu until user exits
    4. Offer to save on exit
    """

    # ── Welcome Banner ────────────────────────────────────────
    print(f"\n  {SEPARATOR}")
    print(f"  {'🎯  FOCUSFLOW: THE GAMIFIED STUDY ENGINE  🎯':^52}")
    print(f"  {SEPARATOR}")
    print(f"  {'Study Hard. Level Up. Defeat Distractions.':^52}")
    print(f"  {SEPARATOR}\n")

    # ── Load Existing Save or Create New Profile ──────────────
    profile = load_data()

    if profile:
        print(f"  ✔   Save file found!  Welcome back, {profile['name']}!")
        show_stats(profile)
    else:
        print("  No save file found — let's create your character!\n")
        name    = input("  Enter your name: ").strip() or "Student"
        profile = create_profile(name)
        print(f"\n  Adventure begins!  Good luck, {profile['name']}! 🚀\n")

    # ── Main Menu (Core while True Loop) ─────────────────────
    # DECOMPOSITION — Each menu option is handled by its own function.
    while True:
        print(f"  {SEPARATOR}")
        print(f"  {'📋  MAIN MENU':^52}")
        print(f"  {SEPARATOR}")
        print("  [1]  Add & Complete a Study Task")
        print("  [2]  View My Stats")
        print("  [3]  Save Progress")
        print("  [4]  Exit")
        print(f"  {SEPARATOR}")

        choice = input("  Choose an option (1-4): ").strip()

        # ── Option 1: Log a Task ──────────────────────────────
        if choice == "1":
            task_name, duration = add_task()
            complete_task(profile, task_name, duration)

        # ── Option 2: View Stats ──────────────────────────────
        elif choice == "2":
            show_stats(profile)

        # ── Option 3: Save ────────────────────────────────────
        elif choice == "3":
            save_data(profile)

        # ── Option 4: Exit ────────────────────────────────────
        elif choice == "4":
            print(f"\n  {SEPARATOR}")

            # Ask whether to save before quitting
            save_choice = input("  Save your progress before exiting? (y/n): ").strip().lower()
            if save_choice == "y":
                save_data(profile)

            print(f"\n  👋  Goodbye, {profile['name']}!")
            print(f"      Final rank : Level {profile['level']}  |  "
                  f"{profile['xp']} XP  |  "
                  f"{profile['total_tasks']} task(s) completed")
            print(f"  {SEPARATOR}")
            print(f"  {'Keep studying. Stay focused. You got this! 💪':^52}")
            print(f"  {SEPARATOR}\n")
            break   # Exit the while True loop → program ends

        # ── Invalid Input ─────────────────────────────────────
        else:
            print("\n  ⚠️   Invalid choice. Please enter 1, 2, 3, or 4.\n")


# ── Entry Point ───────────────────────────────────────────────
if __name__ == "__main__":
    main()
