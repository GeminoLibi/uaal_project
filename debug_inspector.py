# debug_inspector.py
import os
from pywinauto.application import Application
import time

# --- The Target ---
APP_TITLE = "Calculator"
APP_EXECUTABLE = "calc.exe"

print(f"--- Starting PyWinAuto Inspector for: {APP_TITLE} ---")

main_window = None
try:
    # --- New, Robust Connection Logic ---
    try:
        # Try to connect if it's already running
        print("Searching for existing Calculator window...")
        app = Application(backend="uia").connect(title=APP_TITLE, timeout=5)
        print("Connected to existing instance.")
    except Exception:
        # If not running, launch it using the reliable method
        print("No running instance found. Launching new instance...")
        os.system(f'start {APP_EXECUTABLE}')
        time.sleep(3) # Give it time to launch
        app = Application(backend="uia").connect(title=APP_TITLE, timeout=20)
        print("Connected to new instance.")
    
    main_window = app.window(title=APP_TITLE)
    main_window.wait('ready', timeout=20)
    
    print("\n>>> Connection Successful! Window is ready. <<<\n")

    # --- The Definitive Test ---
    # Dump the entire UI tree that pywinauto can see for this window.
    print("--- Dumping UI Tree (this may take a moment) ---")
    main_window.print_control_identifiers(depth=None)
    print("--- End of UI Tree ---")

except Exception as e:
    print(f"\n--- SCRIPT FAILED ---")
    print(f"An error occurred: {e}")

finally:
    try:
        if main_window and main_window.exists():
            main_window.close()
            print("\nCalculator closed.")
    except Exception:
        pass