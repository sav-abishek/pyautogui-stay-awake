# Stay Awake (PyAutoGUI)

Small Python utility to keep your system active by simulating mouse movement and a keyboard tap periodically.

## Features

- Runs for a fixed duration, or indefinitely until interrupted.
- Configurable activity interval and mouse distance.
- Mouse movement modes:
  - `jitter` (default): randomized short move + return.
  - `box`: deterministic square pattern + return.
- Optional keyboard tap each cycle (default key: `f15`).
- Optional Windows native `SetThreadExecutionState` hint to keep system/display awake.
- No cursor drift (movement returns to starting point each cycle).
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

### Add/disable keyboard tap

```bash
python stay-awake.py --key f15
python stay-awake.py --key none
```

### Choose mouse pattern

```bash
python stay-awake.py --mouse-mode jitter
python stay-awake.py --mouse-mode box
```

### Windows execution-state mode

```bash
python stay-awake.py --windows-execution-state
```

## Arguments

- `-t, --time`  
  Total run time in **seconds**.  
  If omitted, script runs until interrupted.

- `-i, --interval` (default: `15.0`)  
  Seconds to wait between activity cycles.

- `-d, --distance` (default: `20`)  
  Pixel range for mouse movement.

- `--key` (default: `f15`)  
  Keyboard key to tap each cycle.  
  Use `none` to disable keyboard taps.

- `--mouse-mode` (default: `jitter`)  
  Mouse pattern: `jitter` or `box`.

- `--windows-execution-state`  
  Windows-only mode that uses native `SetThreadExecutionState` hints.

## Stop Behavior

- Press `Ctrl+C` to stop manually.
- Move the cursor to the **top-left corner** to trigger PyAutoGUI failsafe.

## Note on "Physical" Trackpad Movement

This script sends software-generated input events (via PyAutoGUI), not true hardware events from a physical trackpad.
If your environment ignores synthetic input for lock/idle policy, software movement and key taps may still be ignored.
