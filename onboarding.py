# onboarding.py

import logging
import os

def select_mode():
    logging.info("\n--- Select Operation Mode ---")
    logging.info("  [1] Agentic Mode (Give the AI a high-level goal and let it work)")
    logging.info("  [2] Assisted Mode (Act as the AI's executive controller, giving turn-by-turn commands)")
    while True:
        try:
            choice = int(input("Enter your choice (1 or 2): "))
            if choice == 1: return "agentic"
            if choice == 2: return "assisted"
            logging.warning("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            logging.warning("Invalid input. Please enter a number.")

def select_assisted_mode_type():
    logging.info("\n--- Select Assisted Mode Type ---")
    logging.info("  [1] Analyzed Mode (The AI will analyze the UI and add summaries. Slower but more readable.)")
    logging.info("  [2] Raw Mode (The AI is bypassed for display. You get the raw UI data directly. Faster.)")
    while True:
        try:
            choice = int(input("Enter your choice (1 or 2): "))
            if choice == 1: return "analyzed"
            if choice == 2: return "raw"
            logging.warning("Invalid choice.")
        except ValueError:
            logging.warning("Invalid input.")

def select_model_source():
    logging.info("\n--- Select AI Model Source ---")
    logging.info("  [1] Local Model (Runs on your machine, private and free)")
    logging.info("  [2] API (Uses an external service like OpenAI, requires an API key)")
    while True:
        try:
            choice = int(input("Enter your choice (1 or 2): "))
            if choice == 1: return "local"
            if choice == 2: return "api"
            logging.warning("Invalid choice.")
        except ValueError:
            logging.warning("Invalid input.")

def select_local_model():
    models = [
        {"name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "description": "Tier 1: Ultra-Lightweight", "context_window": 2048},
        {"name": "microsoft/Phi-3-mini-4k-instruct", "description": "Tier 2: Balanced (Recommended)", "context_window": 4096},
        {"name": "meta-llama/Meta-Llama-3-8B-Instruct", "description": "Tier 3: High-Quality", "context_window": 8192},
    ]
    logging.info("\n--- UAAL Local Model Selector ---")
    for i, model in enumerate(models):
        logging.info(f"  [{i+1}] {model['name']} - {model['description']}")
    other_option_index = len(models) + 1
    logging.info(f"  [{other_option_index}] Other (Enter model name manually)")
    while True:
        try:
            choice = int(input(f"Enter your choice (1-{other_option_index}): "))
            if 1 <= choice <= len(models):
                selected_model = models[choice - 1]
                logging.info(f"You selected: {selected_model['name']}")
                return selected_model
            elif choice == other_option_index:
                custom_model_name = input("Enter the full Hugging Face model name: ")
                custom_context_window = int(input("Enter the model's context window size: "))
                return {"name": custom_model_name, "context_window": custom_context_window}
            else:
                logging.warning("Invalid choice.")
        except ValueError:
            logging.warning("Invalid input.")

def select_api_config():
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        logging.info("Found API key in environment variable 'OPENAI_API_KEY'.")
        return {"api_key": api_key}
    else:
        api_key = input("Please enter your API key: ")
        return {"api_key": api_key} if api_key else None

def select_target():
    logging.info("\n--- Select Target ---")
    presets = {
        "desktop": ["Calculator", "Notepad", "File Explorer"],
        "web": ["https://google.com", "https://wikipedia.org", "https://github.com"]
    }
    logging.info("  [1] Select from a preset list")
    logging.info("  [2] Enter a custom target")
    while True:
        try:
            initial_choice = int(input("Enter your choice (1 or 2): "))
            if initial_choice in [1, 2]: break
            else: logging.warning("Invalid choice.")
        except ValueError: logging.warning("Invalid input.")
    
    while True:
        try:
            if initial_choice == 1:
                target_type_choice = int(input("Select target type: [1] Desktop [2] Web: "))
                target_type = "desktop" if target_type_choice == 1 else "web"
                logging.info("\nSelect a preset target:")
                for i, preset in enumerate(presets[target_type]):
                    logging.info(f"  [{i+1}] {preset}")
                preset_choice = int(input(f"Enter your choice (1-{len(presets[target_type])}): "))
                identifier = presets[target_type][preset_choice - 1]
                return {"type": target_type, "identifier": identifier}
            elif initial_choice == 2:
                target_type_choice = int(input("Select target type: [1] Desktop [2] Web: "))
                target_type = "desktop" if target_type_choice == 1 else "web"
                identifier = input(f"Enter the target {'window title' if target_type == 'desktop' else 'URL'}: ")
                return {"type": target_type, "identifier": identifier}
        except (ValueError, IndexError):
            logging.warning("Invalid input. Please try again.")

def start_onboarding():
    logging.info("="*30)
    logging.info("Welcome to the Universal Application Abstraction Layer (UAAL)")
    logging.info("="*30)
    
    config = {}
    config["mode"] = select_mode()

    if config["mode"] == "assisted":
        config["assisted_type"] = select_assisted_mode_type()

    model_source = select_model_source()
    if model_source == "local":
        config["model_config"] = {"type": "local", "details": select_local_model()}
    elif model_source == "api":
        config["model_config"] = {"type": "api", "details": select_api_config()}

    config["target"] = select_target()
    
    logging.info("\nOnboarding complete! Configuration set.")
    return config