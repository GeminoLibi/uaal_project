# uaal_engine/api_analyzer.py

import json
import logging
import os
import requests

class APIAnalyzer:
    def __init__(self, api_key, endpoint_url="https://api.openai.com/v1/chat/completions", model="gpt-4-turbo"):
        logging.info(f"Initializing API Analyzer for model: {model}")
        if not api_key:
            raise ValueError("API key is required for the API Analyzer.")
        self.api_key = api_key
        self.endpoint_url = endpoint_url
        self.model = model
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def _make_api_call(self, messages):
        payload = { "model": self.model, "messages": messages, "temperature": 0.1 }
        try:
            response = requests.post(self.endpoint_url, headers=self.headers, json=payload, timeout=120)
            response.raise_for_status()
            response_json = response.json()
            return response_json['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            return None
        except (KeyError, IndexError) as e:
            logging.error(f"Could not parse API response: {e}. Full response: {response.text}")
            return None

    def analyze_dom(self, ui_dom):
        system_prompt = (
            "You are a UI analysis machine that speaks only JSON. "
            "Your task is to take a list of UI elements and add two new keys to each element: "
            "'predicted_action' (a concise, uppercase verb phrase) and "
            "'summary' (a brief description). "
            "Your response MUST be ONLY the modified JSON object, with no extra text or markdown."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(ui_dom, indent=2)}
        ]
        logging.info("Analyzing UI DOM with external API...")
        response_text = self._make_api_call(messages)
        if not response_text: return None
        try:
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            return json.loads(response_text[json_start:json_end])
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Could not parse JSON from API response. Error: {e}")
            return None
    
    def interpret_command(self, command_str, valid_actions, dom_elements):
        system_prompt = (
            "You are a helpful assistant that corrects user input for a command-line UI automation tool. "
            "Your task is to interpret the user's intent and formulate a single, valid command to accomplish it. "
            "Your entire response MUST be the single corrected command and nothing else. "
            "If the user's intent is unclear or cannot be mapped to a valid action, you MUST respond with the single word: unknown"
        )
        user_prompt = f"""
CONTEXT:
- The user's raw command was: "{command_str}"
- The list of available UI elements is: {json.dumps(dom_elements, indent=2)}
- The list of valid command actions is: {valid_actions}

TASK:
Based on the context, what is the single, corrected command the user was trying to issue?

Corrected command:"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        logging.info(f"Interpreting ambiguous command '{command_str}' with external API...")
        response_text = self._make_api_call(messages)
        if not response_text: return "unknown"
        corrected_command = response_text.strip().replace("`", "").split('\n')[0]
        return corrected_command

    def generate_plan(self, goal, ui_dom):
        logging.warning("generate_plan is not fully implemented yet.")
        return None