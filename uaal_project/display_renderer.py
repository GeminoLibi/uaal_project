# display_renderer.py

import time
import os
import platform

OUTPUT_FILE = 'renderer_output.txt'
CLEAR_COMMAND = 'cls' if platform.system().lower() == "windows" else 'clear'

def main():
    print("--- UAAL Renderer Initialized ---")
    print(f"Watching for updates in '{OUTPUT_FILE}'...")
    time.sleep(2)

    last_mod_time = 0
    
    while True:
        try:
            if os.path.exists(OUTPUT_FILE):
                current_mod_time = os.path.getmtime(OUTPUT_FILE)
                
                if current_mod_time > last_mod_time:
                    os.system(CLEAR_COMMAND)
                    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(content)
                    last_mod_time = current_mod_time
            else:
                if last_mod_time != -1:
                    os.system(CLEAR_COMMAND)
                    print("\n--- Waiting for UI data from the main application... ---")
                    last_mod_time = -1

            time.sleep(0.5)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred in the display renderer: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()