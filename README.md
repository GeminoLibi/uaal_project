# Project Spyglass: The Universal Application Abstraction Layer (UAAL)

An experimental, AI-assisted framework designed to control any GUI application (desktop or web) through a simple, unified, text-based command line. The goal of Spyglass is to create a "de-GUI-fier," abstracting away complex graphical interfaces into a stream of interactable text elements.



## What is Spyglass?

Spyglass acts as a middleware between you and an application. It perceives the visual elements of a GUI, translates them into a simplified text-based "DOM," and allows you to interact with those elements using simple commands. It's built on a tiered driver architecture, designed to use the best possible method for controlling a given application.

## Core Features

* **Cross-Platform Control:** Interact with both native Windows desktop applications and modern web applications through a single interface.
* **Application Switching:** Seamlessly switch control from one application to another (e.g., from a web browser to Notepad) mid-session with the `switch` command.
* **Assisted Mode:** A turn-by-turn, human-in-the-loop mode where you act as the executive agent, guiding the tool with simple commands.
* **Dual-Terminal UI:** Utilizes a main terminal for commands and logs, and a second, clean "renderer" terminal that displays the current text-based view of the target application.
* **Smart Command Interpretation:** Leverages local or API-based LLMs to interpret ambiguous or misspelled commands, translating user intent into valid actions.
* **CAPTCHA Detection:** Can detect the presence of `<iframe>`-based CAPTCHAs, pausing the script to allow for manual user intervention.

## Architecture: The Tiered Driver System

Spyglass is designed around a "Tiered Driver" philosophy, allowing it to use the best tool for the job.

* **Tier 1: Accessibility Drivers (Implemented)**
    * Uses official accessibility APIs to get fast, accurate, structured data from applications.
    * Includes the `WindowsDriver` (built on `pywinauto`) and the `BrowserDriver` (built on `Playwright`).

* **Tier 2: Vision Driver (Planned)**
    * A future driver that will use screenshots and Optical Character Recognition (OCR) to see and read the screen like a human.
    * Intended for applications with non-standard UIs that don't respond to accessibility APIs (e.g., Steam, Discord, games).

* **Tier 3: Interception Driver (Conceptual)**
    * A long-term goal to use advanced techniques like Proxy DLLs to intercept graphics commands before they are rendered, capturing the purest form of UI data.

## Getting Started

### Prerequisites

1.  **Python 3.10+**
2.  **Tesseract OCR Engine:** The Vision Driver will require this. It's recommended to install it now.
    * Download and run the installer from the [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) page.
    * **Important:** During installation, ensure you check the option to add Tesseract to your system's `PATH`.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd uaal_project
    ```

2.  **Create and activate a virtual environment:**
    * On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **(Optional) Set API Key:** If you plan to use an API-based model (like GPT-4), set your API key as an environment variable named `OPENAI_API_KEY`.

## Usage

1.  **Run the application from your terminal:**
    ```bash
    python main.py
    ```
2.  **Follow the Onboarding Prompts:** The script will guide you through selecting a mode, an AI model, and a target application.
3.  **Interact:** A second renderer window will open. Use the main terminal to issue commands based on the UI elements you see.

## Command Reference

| Command                  | Description                                                                                              |
| ------------------------ | -------------------------------------------------------------------------------------------------------- |
| `click <selector>`       | Clicks a UI element. **Example:** `click b25`                                                            |
| `type <text>`            | Types text into the currently focused element (e.g., Notepad). **Example:** `type hello world`             |
| `type <selector> <text>` | Types text into a specific input field. **Example:** `type i3 search query`                                |
| `press <keys>`           | Presses a key or key combination. **Example:** `press ctrl s`                                              |
| `switch <type> <id>`     | Switches control to a new application. **Example:** `switch web https://google.com`                        |
| `Maps <url>`         | (Web Only) Navigates the browser to a new URL. **Example:** `Maps https://news.google.com`         |
| `rescan`                 | Forces a new scan and redraw of the application's UI.                                                    |
| `close` / `minimize`     | (Desktop Only) Executes window actions.                                                                  |
| `help`                   | Displays a list of available commands.                                                                   |
| `exit`                   | Ends the current session and closes the application.                                                     |

## Future Roadmap

* [ ] **Flesh out Agentic Mode:** Improve the planning and execution capabilities for autonomous operation.
* [ ] **Build Tier 2 Vision Driver:** Implement the OCR-based driver to handle non-standard applications.
* [ ] **Improve Complex UI Scanning:** Enhance the Tier 1 `WindowsDriver` to better parse difficult applications like the modern File Explorer.