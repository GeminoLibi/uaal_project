# ua_al_engine/renderer.py

import logging
import subprocess
import os
import platform
import time

class DualTerminalRenderer:
    """
    Manages a separate terminal window to display the rendered UI, creating a
    two-window experience for the user.
    """
    OUTPUT_FILE = 'renderer_output.txt'

    def __init__(self):
        self.renderer_process = None
        self.os_type = platform.system().lower()
        self._launch_renderer_window()

    def _launch_renderer_window(self):
        """Launches the display_renderer.py script in a new terminal window."""
        logging.info("Launching separate renderer window...")
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        display_script_path = os.path.join(project_dir, 'display_renderer.py')
        
        command = ['python', display_script_path]
        
        try:
            if self.os_type == "windows":
                self.renderer_process = subprocess.Popen(
                    ['cmd.exe', '/c', 'start'] + command,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            # ... (macOS and Linux logic remains the same) ...
            
            time.sleep(2)
            logging.info("Renderer window launched.")
        except Exception as e:
            logging.error(f"Failed to launch separate terminal window: {e}")
            self.renderer_process = None

    def update(self, dom_list):
        """Renders the UI DOM to a text file for the display window to read."""
        # This is a public method that calls the private rendering logic
        rendered_text = self._render_to_text(dom_list)
        try:
            with open(self.OUTPUT_FILE, 'w', encoding='utf-8') as f:
                f.write(rendered_text)
        except Exception as e:
            logging.error(f"Failed to write to renderer output file: {e}")

    def _render_to_text(self, dom_list):
        """Takes a DOM list and returns a single formatted string."""
        output_lines = []
        
        for item in dom_list:
            tag = item.get("tag", "unknown").lower()
            text = item.get("text", "").strip()
            short_selector = item.get("short_selector", "")
            command_tag = f"[{short_selector}]" if short_selector else ""

            # --- RENDER HEADERS ---
            if tag.startswith('h'):
                output_lines.append("") # Add a blank line before the header
                output_lines.append(f"=== {text.upper()} ===")
                output_lines.append("") # And a blank line after
            
            # --- RENDER INPUT FIELDS ---
            elif tag in ['input', 'textarea', 'edit']:
                prompt_text = f"{text} " if text else ""
                output_lines.append(f"{prompt_text}{command_tag} [_________________________]")
                output_lines.append("") # Add a blank line after for spacing

            # --- RENDER LIST ITEMS AND PARAGRAPHS ---
            elif tag in ['p', 'li']:
                output_lines.append(f"- {text} {command_tag if tag == 'li' else ''}")

            # --- RENDER LINKS AND BUTTONS ---
            elif tag in ['a', 'button', 'select']:
                line = f"[{text}] {command_tag}" if text else command_tag
                output_lines.append(line)
            
            # --- RENDER GENERIC TEXT ---
            else:
                if text:
                    output_lines.append(f"{text} {command_tag}")

        # Assemble the final string
        header = "--- Rendered Text-Based UI ---\n\n"
        footer = "\n\n------------------------------\n"
        return header + "\n".join(output_lines) + footer
        """Takes a DOM list and returns a single formatted string."""
        output_lines = []
        
        for item in dom_list:
            tag = item.get("tag", "unknown").lower()
            text = item.get("text", "").strip()
            short_selector = item.get("short_selector", "")
            command_tag = f"[{short_selector}]" if short_selector else ""

            # --- RENDER HEADERS ---
            if tag.startswith('h'):
                output_lines.append("") # Add a blank line before the header
                output_lines.append(f"=== {text.upper()} ===")
                output_lines.append("") # And a blank line after
            
            # --- RENDER INPUT FIELDS ---
            elif tag in ['input', 'textarea', 'edit']:
                prompt_text = f"{text} " if text else ""
                output_lines.append(f"{prompt_text}{command_tag} [_________________________]")
                output_lines.append("") # Add a blank line after for spacing

            # --- RENDER LIST ITEMS AND PARAGRAPHS ---
            elif tag in ['p', 'li']:
                output_lines.append(f"- {text} {command_tag if tag == 'li' else ''}")

            # --- RENDER LINKS AND BUTTONS ---
            elif tag in ['a', 'button', 'select']:
                line = f"[{text}] {command_tag}" if text else command_tag
                output_lines.append(line)
            
            # --- RENDER GENERIC TEXT ---
            else:
                if text:
                    output_lines.append(f"{text} {command_tag}")

        # Assemble the final string
        header = "--- Rendered Text-Based UI ---\n\n"
        footer = "\n\n------------------------------\n"
        return header + "\n".join(output_lines) + footer
        """Takes a DOM list and returns a single formatted string."""
        output_lines = []
        current_line = ""
        for item in dom_list:
            tag = item.get("tag", "unknown").lower()
            text = item.get("text", "").strip()
            short_selector = item.get("short_selector", "")
            command_tag = f"[{short_selector}]" if short_selector else ""

            # --- NEW LOGIC FOR INPUT FIELDS ---
            if tag in ['input', 'textarea', 'edit']:
                if text:
                    # Input field with existing text
                    current_line += f" {text} [___{short_selector}___]"
                else:
                    # Empty input field
                    current_line += f" [___{short_selector}___]"
            # --- END NEW LOGIC ---
            elif tag.startswith('h'):
                if current_line: output_lines.append(current_line)
                output_lines.append("")
                output_lines.append(f"== {text} {command_tag} ==")
                output_lines.append("")
                current_line = ""
            elif tag in ['a', 'button', 'select']:
                if text: current_line += f" {text} {command_tag}"
                else: current_line += f" {command_tag}"
            elif tag in ['p', 'li']:
                if current_line: output_lines.append(current_line)
                current_line = text
            else:
                if text: current_line += f" {text}"
        if current_line: output_lines.append(current_line)
        
        # Assemble the final string
        header = "--- Rendered Text-Based UI ---\n\n"
        footer = "\n\n------------------------------\n"
        return header + "\n".join(output_lines) + footer

    def close(self):
        """Closes the separate renderer window."""
        if self.renderer_process and self.renderer_process.poll() is None:
            logging.info("Closing renderer window...")
            try:
                self.renderer_process.terminate()
            except Exception as e:
                logging.error(f"Could not terminate renderer process: {e}")
        if os.path.exists(self.OUTPUT_FILE):
            os.remove(self.OUTPUT_FILE)

# This function is kept for backwards compatibility but is deprecated
def render_dom_as_text(dom_list):
    renderer = DualTerminalRenderer()
    renderer.update(dom_list)
    # Note: In this simple call, closing is not handled automatically.

