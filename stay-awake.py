import argparse
import random
import sys
import time
from dataclasses import dataclass

import pyautogui


# Windows execution-state flags used to hint the OS to stay awake.
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


@dataclass
class RuntimeConfig:
    total_time: float | None
    interval: float
    distance: int
    key_to_tap: str | None
    mouse_mode: str
    use_windows_execution_state: bool


def parse_args() -> RuntimeConfig:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the system active by simulating mouse and keyboard activity. "
            "Runs until interrupted unless --time is provided."
        )
    )
    parser.add_argument(
        "-t",
        "--time",
        type=float,
        default=None,
        help="Total run time in seconds. Omit to run until Ctrl+C.",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=15.0,
        help="Seconds to wait between activity cycles (default: 15).",
    )
    parser.add_argument(
        "-d",
        "--distance",
        type=int,
        default=20,
        help="Pixels to move per step (default: 20).",
    )
    parser.add_argument(
        "--key",
        type=str,
        default="f15",
        help=(
            "Keyboard key to tap once per cycle (default: f15). "
            "Use 'none' to disable key taps."
        ),
    )
    parser.add_argument(
        "--mouse-mode",
        choices=["box", "jitter"],
        default="jitter",
        help=(
            "Mouse movement pattern. 'jitter' adds small randomized moves; "
            "'box' keeps the original deterministic square pattern."
        ),
    )
    parser.add_argument(
        "--windows-execution-state",
        action="store_true",
        help=(
            "Windows-only: call SetThreadExecutionState to keep system/display awake "
            "between synthetic inputs."
        ),
    )
    args = parser.parse_args()

    if args.time is not None and args.time <= 0:
        parser.error("--time must be greater than 0.")
    if args.interval <= 0:
        parser.error("--interval must be greater than 0.")
    if args.distance <= 0:
        parser.error("--distance must be greater than 0.")

    key = args.key.strip().lower()
    key_to_tap: str | None
    if key == "none":
        key_to_tap = None
    else:
        if key not in set(pyautogui.KEYBOARD_KEYS):
            parser.error(
                f"--key '{args.key}' is not a valid PyAutoGUI key. "
                "Use a key listed in pyautogui.KEYBOARD_KEYS or 'none'."
            )
        key_to_tap = key

    if args.windows_execution_state and sys.platform != "win32":
        parser.error("--windows-execution-state is only supported on Windows.")

    return RuntimeConfig(
        total_time=args.time,
        interval=args.interval,
        distance=args.distance,
        key_to_tap=key_to_tap,
        mouse_mode=args.mouse_mode,
        use_windows_execution_state=args.windows_execution_state,
    )


def sleep_with_deadline(seconds: float, deadline: float | None) -> bool:
    """Sleep in short chunks and stop early if the deadline is reached."""
    remaining = seconds
    while remaining > 0:
        if deadline is not None and time.monotonic() >= deadline:
            return False
        step = min(0.5, remaining)
        time.sleep(step)
        remaining -= step
    return True


def set_windows_execution_state(enabled: bool) -> None:
    """Toggle Windows execution-state hints for keeping the system awake."""
    if sys.platform != "win32":
        return

    import ctypes

    flags = ES_CONTINUOUS
    if enabled:
        flags |= ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED

    result = ctypes.windll.kernel32.SetThreadExecutionState(flags)
    if result == 0:
        state = "enable" if enabled else "disable"
        raise OSError(f"Failed to {state} Windows execution state.")


def perform_mouse_activity(distance: int, direction: int, mouse_mode: str) -> int:
    """Perform one mouse cycle and return the next direction."""
    if mouse_mode == "box":
        x_step = distance * direction
        y_step = distance * direction
        pyautogui.moveRel(x_step, 0, duration=0.1)
        pyautogui.moveRel(0, y_step, duration=0.1)
        pyautogui.moveRel(-x_step, 0, duration=0.1)
        pyautogui.moveRel(0, -y_step, duration=0.1)
        return -direction

    # Randomized short move with return path for a more natural pattern.
    dx = random.randint(-distance, distance)
    dy = random.randint(-distance, distance)
    if dx == 0 and dy == 0:
        dx = 1

    out_duration = random.uniform(0.06, 0.2)
    back_duration = random.uniform(0.06, 0.2)
    pyautogui.moveRel(dx, dy, duration=out_duration)
    pyautogui.moveRel(-dx, -dy, duration=back_duration)
    return direction


def perform_key_activity(key_to_tap: str | None) -> None:
    if key_to_tap is None:
        return
    pyautogui.press(key_to_tap)


def main() -> None:
    config = parse_args()

    pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort quickly.
    deadline = (
        time.monotonic() + config.total_time if config.total_time is not None else None
    )

    if config.total_time is None:
        print("Running until interrupted (Ctrl+C).")
    else:
        print(f"Running for {config.total_time:.1f} seconds.")

    print(f"Mouse mode: {config.mouse_mode} | Key tap: {config.key_to_tap or 'disabled'}")
    if config.use_windows_execution_state:
        print("Windows execution-state hint enabled.")
    print("Press Ctrl+C to stop.")

    direction = 1

    try:
        if config.use_windows_execution_state:
            set_windows_execution_state(True)

        while True:
            if deadline is not None and time.monotonic() >= deadline:
                break

            direction = perform_mouse_activity(
                distance=config.distance,
                direction=direction,
                mouse_mode=config.mouse_mode,
            )
            perform_key_activity(config.key_to_tap)

            if not sleep_with_deadline(config.interval, deadline):
                break
    except KeyboardInterrupt:
        print("\nStopped by user.")
        return
    except pyautogui.FailSafeException:
        print("\nPyAutoGUI failsafe triggered (mouse moved to top-left corner).")
        return
    finally:
        if config.use_windows_execution_state:
            try:
                set_windows_execution_state(False)
            except OSError as exc:
                print(f"Warning: could not clear Windows execution state cleanly: {exc}")

    print("Completed.")


if __name__ == "__main__":
    main()
