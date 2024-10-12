# conversation_manager.py
import copy
import json
import re
import openai
import prompt  # Ensure you have a prompt.py file containing the required prompts

class ConversationManager:
    def __init__(self, api_key: str, user_name: str = "User"):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.user_name = user_name
        self.name = prompt.char_name
        self.Likeability = 0
        self.Mental = 70
        self.dialogue = ""
        self.expression = "Neutral"
        self.thinking = ""
        self.location = ""
        self.translated_text = ""

        # Quest Status
        self.quests = {}

        self.world_situation = {
            "Time": "Morning",
            "Location": "Maid Café 'Hoshizora'",
            "Environment": "Calm, pleasant",
            "Atmosphere": "Welcoming",
            "Surrounding Condition": "Few customers around"
        }

        self.conversation_history = [{"role": "system", "content": self.build_system_prompt()}]

    def send_message_to_api(self, user_message: str):
        self.update_world_situation()
        request_data = self.prepare_api_request(user_message)
        response = self.make_api_request(request_data)

        if response["success"]:
            self.process_api_response(response["content"])
            return self.dialogue
        else:
            return f"Error: {response['content']}"

    def prepare_api_request(self, user_message: str) -> dict:
        user_status = prompt.user_status_prompt.format(dialogue=user_message)
        self.add_message("user", user_status)

        world_status = self.format_world_status()
        char_status = prompt.char_status_prompt.format(likeability=self.Likeability, mental=self.Mental)

        api_conversation_history = copy.deepcopy(self.conversation_history)
        api_conversation_history[-1]['content'] = (
            world_status + "\n" +
            user_status + "\n" +
            char_status + "\n" +
            prompt.post_history_instructions
        )

        system_prompt = self.build_system_prompt()
        return {
            "messages": [{"role": "system", "content": system_prompt}] + api_conversation_history
        }

    def make_api_request(self, request_data: dict) -> dict:
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=request_data["messages"],
                max_tokens=250,
                temperature=0.7
            )
            return {"success": True, "content": response.choices[0].message.content}
        except Exception as e:
            return {"success": False, "content": str(e)}

    def process_api_response(self, api_response: str):
        # Extract and update the attributes from the API response
        likeability_match = re.search(r"Likeability: (\d+)", api_response)
        mental_match = re.search(r"Mental: (\d+)", api_response)

        if likeability_match:
            self.Likeability = int(likeability_match.group(1))
        if mental_match:
            self.Mental = int(mental_match.group(1))

        dialogue_match = re.search(r"Speaking: (.+?)(?=\n|$)", api_response, re.DOTALL)
        if dialogue_match:
            self.dialogue = dialogue_match.group(1).strip()

        expression_match = re.search(r"Expressions: (.+?)(?=\n|$)", api_response, re.DOTALL)
        if expression_match:
            self.expression = expression_match.group(1).strip()
        else:
            self.expression = api_response.strip()

        thinking_match = re.search(r"Thinking: (.+?)(?=\n|$)", api_response, re.DOTALL)
        if thinking_match:
            self.thinking = thinking_match.group(1).strip()
        else:
            self.thinking = api_response.strip()

        # Extract quest status
        self.update_quest_status(api_response)

    def update_quest_status(self, api_response: str):
        quest_status_pattern = r"Quest Name: (.+?)\nQuest Status: (.+?)(?=\n|$)"
        quest_matches = re.findall(quest_status_pattern, api_response)

        for quest_name, quest_status in quest_matches:
            self.quests[quest_name] = quest_status

    def format_world_status(self) -> str:
        return prompt.world_status_prompt.format(
            time=self.world_situation["Time"],
            location=self.world_situation["Location"],
            environment=self.world_situation["Environment"],
            atmosphere=self.world_situation["Atmosphere"],
            surround_cond=self.world_situation["Surrounding Condition"]
        )

    def build_system_prompt(self):
        quest_descriptions = "\n".join([f"{quest}: {status}" for quest, status in self.quests.items()])
        return prompt.start_prompt.replace("{{char}}", self.name).replace("{{user}}", self.user_name).format(
            description=prompt.description + f"\n\n### Current Quests\n{quest_descriptions}"
        )
    def update_world_situation(self):
        # Dynamically update world situation if required (e.g., time of day)
        self.world_situation["Time"] = "Afternoon"  # Example update

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
