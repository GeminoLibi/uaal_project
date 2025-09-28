# uaal_engine/semantic_analyzer.py

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import json
import logging

class SemanticAnalyzer:
    def __init__(self, model_name="microsoft/Phi-3-mini-4k-instruct"):
        logging.info(f"Initializing Semantic Analyzer with model: {model_name}.")
        self.pipe = pipeline(
            "text-generation",
            model=model_name,
            model_kwargs={"torch_dtype": "auto"},
            device_map="auto",
        )
        logging.info("Model loaded successfully.")

    def analyze_dom(self, ui_dom):
        system_prompt = (
            "You are a UI analysis machine that speaks only JSON. "
            "Your task is to take a list of UI elements and add two new keys to each element: "
            "'predicted_action' (a concise, uppercase verb phrase) and "
            "'summary' (a brief description). "
            "Your response MUST be ONLY the modified JSON object, with no extra text."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(ui_dom, indent=2)}
        ]
        logging.info("Analyzing UI DOM with local AI model...")
        output = self.pipe(messages, max_new_tokens=4096, eos_token_id=self.pipe.tokenizer.eos_token_id, do_sample=False)
        response_text = output[0]['generated_text'][-1]['content']
        try:
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            return json.loads(response_text[json_start:json_end])
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Could not parse JSON from model response. Error: {e}")
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
        logging.info(f"Interpreting ambiguous command '{command_str}' with AI...")
        try:
            output = self.pipe(
                messages,
                max_new_tokens=50,
                eos_token_id=self.pipe.tokenizer.eos_token_id,
                do_sample=False,
                pad_token_id=self.pipe.tokenizer.eos_token_id
            )
            response_text = output[0]['generated_text'][-1]['content']
            corrected_command = response_text.strip().replace("`", "").split('\n')[0]
            return corrected_command
        except Exception as e:
            logging.error(f"An error occurred during AI command interpretation: {e}")
            return "unknown"

    def generate_plan(self, goal, ui_dom):
        logging.warning("generate_plan is not fully implemented yet.")
        return None