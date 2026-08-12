import os
import subprocess
import datetime
import time
from pathlib import Path

# Setup Paths
ROOT_DIR = Path(__file__).resolve().parent
BOT_SCRIPT = ROOT_DIR / "live_bot.py"
ENV_FILE = ROOT_DIR / ".env"

def load_env():
    """Load environment variables from .env file securely for scheduled tasks."""
    if ENV_FILE.exists():
        with open(ENV_FILE, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, val = line.strip().split("=", 1)
                    os.environ[key] = val.strip(' "\'')

def run_supervisor():
    print("==================================================")
    print("    MASTER TQQQ ENGINE - INTRADAY SUPERVISOR      ")
    print("==================================================")
    
    load_env()
    
    print(f"\n[{datetime.datetime.now().isoformat()}] --- Starting live_bot.py ---")
    
    # Run the bot in a loop in case of unhandled fatal crashes
    # Because this is a scheduled task that runs during market hours, we want it to stay alive
    # The bot handles its own sleep cycles until market opens/closes.
    # However, to be safe, the scheduled task should probably just run it once.
    # If the bot crashes, we restart it.
    
    env = os.environ.copy()
    
    # We will run the bot. Since live_bot.py has an infinite while True loop, 
    # it will run indefinitely. We just need to make sure we restart it if it dies unexpectedly.
    
    while True:
        try:
            print(f"[{datetime.datetime.now().isoformat()}] Launching subprocess...")
            proc = subprocess.run(
                ["python", str(BOT_SCRIPT)],
                cwd=str(ROOT_DIR),
                env=env,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[{datetime.datetime.now().isoformat()}] --- live_bot.py FAILED (Exit Code: {e.returncode}) ---")
            print("Restarting in 60 seconds...")
            time.sleep(60)
        except KeyboardInterrupt:
            print("Supervisor stopped by user.")
            break

if __name__ == "__main__":
    run_supervisor()
