# Stay Awake (PyAutoGUI)

Small Python utility to keep your system active by moving the mouse periodically.

## Features

- Runs for a fixed duration, or indefinitely until interrupted.
- Configurable move interval and distance.
- No cursor drift (moves in a small box and returns to start).
- Safe stop with:
  - `Ctrl+C`
  - PyAutoGUI failsafe (move mouse to top-left corner).

## Requirements

- Python 3.10+
- `pyautogui`

Install dependency:

```bash
pip install pyautogui
```

## Usage

Run from this folder:

```bash
python stay-awake.py
```

This runs until you stop it with `Ctrl+C`.

### Run for a specific time

```bash
python stay-awake.py --time 600
```

Runs for `600` seconds (10 minutes).

### Customize interval and distance

```bash
python stay-awake.py --time 1800 --interval 15 --distance 20
```

## Arguments

- `-t, --time`  
  Total run time in **seconds**.  
  If omitted, script runs until interrupted.

- `-i, --interval` (default: `15.0`)  
  Seconds to wait between move cycles.

- `-d, --distance` (default: `20`)  
  Pixels moved per step in each direction.

## Stop Behavior

- Press `Ctrl+C` to stop manually.
- Move the cursor to the **top-left corner** to trigger PyAutoGUI failsafe.
