import json
import copy
import re
import io
from typing import List, Dict
import requests
from IPython.display import Audio, display
from deep_translator import GoogleTranslator
import src.prompt as prompt
import src.api as chatapi
import src.server as server

class SystemModule:
    def __init__(self, prompt, char_name="ほしかわ"):
        self.char_name = char_name
        self.user_name = ""
        self.world_situation = {
            "Time": "Late Afternoon",
            "Location": "Maid Cafe",
            "Environment": "Maid cafe on the verge of collapse",
            "Atmosphere": "Desperately waiting for new customers",
            "Surrounding Condition": "Quiet and boring"
        }
        # Define the initial prompts and settings
        self.world_status_prompt = prompt.world_status_prompt
        self.user_status_prompt = prompt.user_status_prompt
        self.char_status_prompt = prompt.char_status_prompt

        # Character parameters
        self.Likeability = 20
        self.Mental = 50
        self.processed_prompt = prompt.start_prompt.format(description=prompt.description)

    def set_user_name(self, name):
        self.user_name = name

    def build_prompt(self, user_message: str) -> Dict:
        # Generate the required status prompts
        user_status = self.user_status_prompt.format(dialogue=user_message)
        world_status = self.world_status_prompt.format(
            time=self.world_situation["Time"],
            location=self.world_situation["Location"],
            environment=self.world_situation["Environment"],
            atmosphere=self.world_situation["Atmosphere"],
            surround_cond=self.world_situation["Surrounding Condition"]
        )
        char_status = self.char_status_prompt.format(likeability=self.Likeability, mental=self.Mental)

        # Return the formatted inputs for the conversational module
        return {
            "user_status": user_status,
            "world_status": world_status,
            "char_status": char_status,
            "base_prompt": self.processed_prompt
        }

    def update_character_state(self, api_response: str):
        likeability_match = re.search(r"Likeability: (\d+)", api_response)
        mental_match = re.search(r"Mental: (\d+)", api_response)

        if likeability_match:
            self.Likeability = int(likeability_match.group(1))
        if mental_match:
            self.Mental = int(mental_match.group(1))

    def format_prompt_for_api(self, messages, system_prompt):
        return {
            "messages": [{"role": "system", "content": system_prompt}] + messages
        }

class ConversationalModule:
    def __init__(self):
        self.expression = ""
        self.dialogue = ""
        self.thinking = ""
        self.location = ""
        self.translator = GoogleTranslator(source='ja', target='ko')
        self.translated_text = ""

    def generate_response(self, inputs: Dict[str, str], api_response: str):
        self.extract_response_details(api_response)
        # Generate dialogue using state and emotional inputs
        self.translated_text = self.translator.translate(self.dialogue)
        return {
            "Emotion": self.extract_field(api_response, "Emotion"),
            "Expressions": self.expression,
            "Thinking": self.thinking,
            "Speaking": self.dialogue,
            "Want Location": self.location,
            "Translated Dialogue": self.translated_text
        }

    def extract_response_details(self, api_response: str):
        dialogue_match = re.search(r"Speaking: (.+?)(?=\n|$)", api_response, re.DOTALL)
        self.dialogue = dialogue_match.group(1).strip() if dialogue_match else ""

        expression_match = re.search(r"Expressions: (.+?)(?=\n|$)", api_response, re.DOTALL)
        self.expression = expression_match.group(1).strip() if expression_match else ""

        thinking_match = re.search(r"Thinking: (.+?)(?=\n|$)", api_response, re.DOTALL)
        self.thinking = thinking_match.group(1).strip() if thinking_match else ""

        location_match = re.search(r"Want Location: (.+?)(?=\n|$)", api_response, re.DOTALL)
        self.location = location_match.group(1).strip() if location_match else ""

    def extract_field(self, text: str, field_name: str) -> str:
        match = re.search(f"{field_name}: (.+?)(?=\n|$)", text, re.DOTALL)
        return match.group(1).strip() if match else ""

class RisuAIManager:
    def __init__(self, prompt, translator):
        # Initialize modules
        self.system_module = SystemModule(prompt)
        self.conversational_module = ConversationalModule(translator)

        self.conversation_history = []

    def set_user_name(self, name):
        self.system_module.set_user_name(name)

    def process_user_message(self, user_message: str):
        # Build system prompt
        system_inputs = self.system_module.build_prompt(user_message)

        # Combine into a full API request prompt
        full_prompt = self.system_module.format_prompt_for_api(
            self.conversation_history,
            system_inputs["base_prompt"]
        )
        
        # Simulate API response (replace with actual API call)
        simulated_response = self.mock_api_response()  # Replace with actual API response function

        # Process the API response to update character states
        self.system_module.update_character_state(simulated_response)

        # Generate the conversational module's output based on API response
        char_response = self.conversational_module.generate_response(system_inputs, simulated_response)

        # Output the formatted response details
        print(json.dumps(char_response, indent=2, ensure_ascii=False))

    def mock_api_response(self):
        # Simulated response structure from API
        return """
        Emotion: Nervous
        Expressions: surprise
        Thinking: 오늘의 첫 손님이야!
        Speaking: "私たちのメイドカフェにようこそ！"
        Want Location: Picture
        Likeability: 22
        Mental: 60
        """
