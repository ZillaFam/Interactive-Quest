# Interactive Quest desktop prototype

Double-click `dist\InteractiveQuest.exe` to run the standalone Windows app.
It bundles Python; no console or separate Python installation is needed.
Windows Application Control blocked this unsigned executable during local testing.
No security settings were changed. The Python source version was tested separately.

If using the source: run `python main.py`, or double-click `Launch Quest.vbs`
on this computer (requires its existing Python installation).

Drag the title bar or the panel header to move it. It stays above ordinary
windows. Use Auto to enable automatic play, and X to quit.
The plain blocks are character/enemy placeholders; no final art is included.

Every global keyboard key-down (including key repeat) and mouse button-down
triggers one action. No cooldown or action cap. Movement alone does not count.
Input switches to active; 10 seconds of inactivity resumes auto. Auto fights,
earns combat XP and gold, collects loot, sells it, and returns to battle.
Only timestamps are passed to the game: no key contents, coordinates, window
names, clipboard contents, network connection, or input logs.

Placeholder tuning: 5 HP per enemy, 1 damage per input, 1 XP + 1 gold +
1 loot per kill. Loot sells for 1 gold. Each kill leads to market; the next
action sells and returns. Auto acts once per second.

No quest content, named stats, special items, or leveling rules have been
added. Quest/stat active-only restrictions exist as engine hooks.
Progress is in memory and resets when closed.

Checks: `python -m unittest -v`
Rebuild: `python -m PyInstaller --noconfirm --onefile --windowed --name InteractiveQuest main.py`
