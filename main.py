# main.py

import logging
from uaal_engine.windows_driver import WindowsDriver
from uaal_engine.browser_driver import BrowserDriver
from uaal_engine.semantic_analyzer import SemanticAnalyzer
from uaal_engine.api_analyzer import APIAnalyzer
from uaal_engine.logger_setup import setup_logger
from uaal_engine.renderer import DualTerminalRenderer
from onboarding import start_onboarding
import json
import time

def run_agentic_mode(driver, analyzer, context_window):
    """
    Runs the agent in a self-contained mode where it formulates and executes
    a plan based on a single high-level goal.
    """
    if isinstance(driver, BrowserDriver):
        logging.warning("Agentic mode for web is a future enhancement.")
        return
    USER_GOAL = input("\nPlease state your high-level goal for the AI: ")
    logging.info(f"AGENT: Received goal: '{USER_GOAL}'")
    
    logging.info("PERCEIVING: Analyzing current UI state...")
    ui_dom_result = driver.get_ui_dom(context_window=context_window, apply_limits=True)
    analyzed_dom = analyzer.analyze_dom(ui_dom_result["dom"])
    if not analyzed_dom:
        logging.error("AGENT: Could not analyze the UI. Aborting.")
        return

    plan = analyzer.generate_plan(USER_GOAL, analyzed_dom)
    if not plan:
        logging.error("AGENT: Could not generate a plan. Aborting.")
        return

    logging.info("AGENT: I have a plan:")
    logging.info(json.dumps(plan, indent=2))
    logging.info("AGENT: Executing plan...")
    dom_map = {item["short_selector"]: item["internal_selector"] for item in analyzed_dom}
    for step in plan:
        internal_selector = dom_map.get(step.get('short_selector'))
        if not internal_selector:
            logging.error(f"Could not find selector '{step.get('short_selector')}' from plan.")
            continue
        
        if step.get("command") == "click":
            driver.click(auto_id=internal_selector)
        elif step.get("command") == "type":
            driver.type_text(auto_id=internal_selector, text=step['text'])
        time.sleep(0.5)
    
    logging.info("AGENT: Plan execution complete.")


def _execute_assisted_command(command_str, driver, dom_map, is_web):
    """Helper to execute a parsed command string."""
    parts = command_str.strip().lower().split()
    action = parts[0] if parts else ''
    if not action: return {'action_taken': False}

    special_actions = ["back", "forward", "refresh", "minimize", "maximize", "close"]
    if action in special_actions:
        if hasattr(driver, action):
            getattr(driver, action)()
            if action == 'close' and not is_web: return {'action_taken': True, 'should_break': True}
            return {'action_taken': True}
        else:
            logging.warning(f"Action '{action}' is not supported by the current driver.")
            return {'action_taken': False}
    
    elif action == "navigate":
        if is_web and len(parts) > 1:
            driver.navigate(parts[1])
            return {'action_taken': True}
        else:
            logging.warning("'navigate' is for web targets and requires a URL.")
            return {'action_taken': False}
    
    elif action == "press":
        if len(parts) > 1:
            driver.press_key("+".join(parts[1:]))
            return {'action_taken': True}
        else:
            logging.error("Invalid 'press' command. Must include key(s) to press.")
            return {'action_taken': False}

    elif action == "click":
        if len(parts) < 2:
            logging.error("Invalid 'click' command. Must include a selector.")
            return {'action_taken': False}
        short_selector = parts[1]
        internal_selector = dom_map.get(short_selector)
        if not internal_selector:
            logging.error(f"Selector '{short_selector}' not found.")
            return {'action_taken': False}
        if is_web: driver.click(selector=internal_selector)
        else: driver.click(auto_id=internal_selector)
        return {'action_taken': True}

    elif action == "type":
        if len(parts) < 2:
            logging.error("Invalid 'type' command. Must include text to type.")
            return {'action_taken': False}

        text_to_type_parts = parts[1:]
        target_selector = None
        potential_selector = parts[1]

        if potential_selector in dom_map:
            target_selector = dom_map.get(potential_selector)
            text_to_type_parts = parts[2:]
        
        text_to_type = " ".join(text_to_type_parts)

        if target_selector:
            if is_web: driver.type_text(selector=target_selector, text=text_to_type)
            else: driver.type_text(auto_id=target_selector, text=text_to_type)
        else:
            if hasattr(driver, 'type_global'):
                driver.type_global(text=text_to_type)
            else:
                logging.warning(f"Typing without a selector is not supported by this driver.")
        
        return {'action_taken': True}

    return {'action_taken': False}


def run_assisted_mode(driver, renderer, analyzer, context_window, assisted_type="analyzed"):
    is_web = isinstance(driver, BrowserDriver)
    current_dom = None
    dom_map = {} 
    
    valid_actions = ['click', 'type', 'press', 'navigate', 'exit', 'help', 'rescan', 'switch',
                     'back', 'forward', 'refresh', 'minimize', 'maximize', 'close']

    while True:
        if current_dom is None:
            logging.info("PERCEIVING: Analyzing current UI state...")
            apply_limits = (assisted_type == "analyzed")

            perception_result = driver.get_ui_dom(context_window=context_window, apply_limits=apply_limits)
            ui_dom = perception_result["dom"]
            captcha_detected = perception_result.get("captcha_detected", False)

            if captcha_detected:
                logging.warning("="*50)
                logging.warning("!!! CAPTCHA DETECTED !!!")
                logging.warning("The script will now pause. Please switch to the browser")
                logging.warning("window, solve the CAPTCHA, then return to this terminal.")
                logging.warning("="*50)
                input("--> After solving, press Enter here to continue...")
                current_dom = None
                continue
            
            if assisted_type == "analyzed":
                current_dom = analyzer.analyze_dom(ui_dom)
            else:
                current_dom = ui_dom

            if not current_dom: 
                logging.error("Could not get or analyze the DOM.")
                time.sleep(2)
                continue
            
            dom_map = {item["short_selector"]: item.get("internal_selector") for item in current_dom}
            renderer.update(current_dom)
            
            logging.info(f"--- Current UI State ({assisted_type.upper()}) ---")
            display_dom = [{k: v for k, v in item.items() if k != 'internal_selector'} for item in current_dom]
            logging.info(json.dumps(display_dom, indent=2))
        
        logging.info("AWAITING COMMAND...")
        command_str = input("> ").strip()
        if not command_str: continue

        parts = command_str.lower().split()
        action = parts[0] if parts else ''

        try:
            result = None
            if action == 'help':
                help_text = """
--- Available Commands ---
- click <selector>          : Clicks an element (e.g., click b1).
- type <text>               : Types text into the focused element (e.g., Notepad).
- type <selector> <text>    : Types text into a specific element.
- press <keys>              : Presses a key or combination (e.g., press ctrl s).
- navigate <url>            : (Web Only) Navigates to a new URL.
- switch <type> <id>        : Switches to new target (e.g., switch desktop Calculator).
- rescan                    : Forces a refresh of the current UI view.
- help                      : Displays this help message.
- exit                      : Ends the entire session.
--------------------------"""
                for line in help_text.strip().split('\n'):
                    logging.info(line.strip())
                continue
            
            if action == 'switch':
                if len(parts) < 3:
                    logging.error("Invalid switch command. Usage: switch <type> <identifier>")
                    continue
                target_type = parts[1]
                identifier = " ".join(parts[2:])
                if target_type not in ['desktop', 'web']:
                    logging.error("Invalid target type. Must be 'desktop' or 'web'.")
                    continue
                return {'action': 'switch', 'target': {'type': target_type, 'identifier': identifier}}

            if action in ['exit', 'quit']:
                return {'action': 'exit'}

            if action == 'rescan':
                current_dom = None
                continue

            if action in valid_actions:
                result = _execute_assisted_command(command_str, driver, dom_map, is_web)
            else:
                # AI Fallback Logic (if implemented)
                logging.warning(f"Unknown command: '{action}'")
                result = {'action_taken': False}

            if result and result.get('action_taken'):
                current_dom = None
                if result.get('should_break'):
                    return {'action': 'exit'}
                time.sleep(1.5)

        except (IndexError, Exception) as e:
            logging.error(f"Error executing command '{command_str}': {e}")
    
    return {'action': 'exit'}


def main():
    setup_logger()
    config = start_onboarding()
    
    driver = None
    renderer = DualTerminalRenderer()

    try:
        while True:
            session_result = None
            try:
                target_type = config["target"]["type"]
                if target_type == "desktop":
                    driver = WindowsDriver()
                elif target_type == "web":
                    driver = BrowserDriver()

                analyzer = None
                if config["mode"] in ["agentic", "assisted"]:
                    model_config = config.get("model_config")
                    if model_config and model_config["type"] == "local":
                        analyzer = SemanticAnalyzer(model_name=model_config["details"]["name"])
                    elif model_config and model_config["type"] == "api":
                        analyzer = APIAnalyzer(api_key=model_config["details"]["api_key"])
                
                if not driver or not analyzer:
                    logging.critical("Driver or Analyzer could not be initialized. Exiting.")
                    return

                driver.connect_to_app(config["target"]["identifier"])
                
                model_context_window = config.get("model_config", {}).get("details", {}).get("context_window", 8192)

                run_mode_args = { 
                    "driver": driver, 
                    "renderer": renderer,
                    "analyzer": analyzer, 
                    "context_window": model_context_window 
                }

                if config["mode"] == "assisted":
                    run_mode_args["assisted_type"] = config.get("assisted_type", "raw")
                    session_result = run_assisted_mode(**run_mode_args)
                else:
                    run_agentic_mode(**run_mode_args)
                    session_result = {'action': 'exit'}

            finally:
                if driver and hasattr(driver, 'cleanup'):
                    driver.cleanup()
                    logging.info("Driver for the current session has been cleaned up.")

            if session_result and session_result.get('action') == 'switch':
                config['target'] = session_result['target']
                logging.info(f"--- SWITCHING TARGET TO: {config['target']['identifier']} ---")
            else:
                break

    finally:
        renderer.close()
        logging.info("AGENT: Session ended.")

if __name__ == "__main__":
    main()