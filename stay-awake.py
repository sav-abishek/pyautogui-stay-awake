import argparse
import time

import pyautogui


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Move the mouse periodically to keep the system active. "
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
        help="Seconds to wait between move cycles (default: 15).",
    )
    parser.add_argument(
        "-d",
        "--distance",
        type=int,
        default=20,
        help="Pixels to move per step in each direction (default: 20).",
    )
    args = parser.parse_args()

    if args.time is not None and args.time <= 0:
        parser.error("--time must be greater than 0.")
    if args.interval <= 0:
        parser.error("--interval must be greater than 0.")
    if args.distance <= 0:
        parser.error("--distance must be greater than 0.")

    return args


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


def main() -> None:
    args = parse_args()

    pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort quickly.
    deadline = time.monotonic() + args.time if args.time is not None else None

    if args.time is None:
        print("Running until interrupted (Ctrl+C).")
    else:
        print(f"Running for {args.time:.1f} seconds.")
    print("Press Ctrl+C to stop.")

    direction = 1
    try:
        while True:
            if deadline is not None and time.monotonic() >= deadline:
                break

            # Move in a tiny box and return to start to avoid cursor drift.
            x_step = args.distance * direction
            y_step = args.distance * direction
            pyautogui.moveRel(x_step, 0, duration=0.1)
            pyautogui.moveRel(0, y_step, duration=0.1)
            pyautogui.moveRel(-x_step, 0, duration=0.1)
            pyautogui.moveRel(0, -y_step, duration=0.1)
            direction *= -1

            if not sleep_with_deadline(args.interval, deadline):
                break
    except KeyboardInterrupt:
        print("\nStopped by user.")
        return
    except pyautogui.FailSafeException:
        print("\nPyAutoGUI failsafe triggered (mouse moved to top-left corner).")
        return

    print("Completed.")


if __name__ == "__main__":
    main()
