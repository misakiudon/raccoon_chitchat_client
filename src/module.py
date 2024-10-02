import json
import copy
import re
import io
from typing import List, Dict
import requests
from IPython.display import Audio, display
import src.prompt as prompt
import src.api as chatapi
import src.server as server
from deep_translator import GoogleTranslator

class RisuAIManager:
    def __init__(self):
        self.user_name = ""
        self.claude = chatapi.GPT4OpenAI()
        self.conversation_history: List[Dict[str, str]] = []
        self.max_context_tokens = 4000

        self.name = prompt.char_name  # char_name은 사전에 정의되어 있어야 합니다
        self.world_situation = {
            "Time": "Late Afternoon", "Location": "Made Cafe", "Environment": "Maid cafe on the verge of collapse",
            "Atmosphere": "Desperately waiting for new customers",
            "Surrounding Condition": "Quiet and boring"
        }
        self.world_status_prompt = self.process_script(prompt.world_status_prompt)
        self.user_status_prompt = self.process_script(prompt.user_status_prompt)
        self.char_status_prompt = self.process_script(prompt.char_status_prompt)

        self.first_mes = self.process_script(prompt.first_mes)
        self.description = self.process_script(prompt.description)

        self.Likeability = 20
        self.Mental = 50
        self.expression = ""
        self.dialogue = ""
        self.thinking = ""
        self.location = ""
        self.translator = GoogleTranslator(source='ja', target='ko')
        self.translated_text = ""

    def set_user_name(self, name):
        self.user_name = name
        self.update_prompts()  # 사용자 이름이 설정된 후 프롬프트 업데이트

    def update_prompts(self):
        self.world_status_prompt = self.process_script(prompt.world_status_prompt)
        self.user_status_prompt = self.process_script(prompt.user_status_prompt)
        self.char_status_prompt = self.process_script(prompt.char_status_prompt)
        self.first_mes = self.process_script(prompt.first_mes)
        self.description = self.process_script(prompt.description)

        # TTS 관련 설정
        self.TTS_SERVER_URL = server.TTS_SERVER_URL  # 실제 URL로 교체해야 합니다
        self.model_id = server.model_id  # 적절한 model_id로 교체
        self.speaker_id = server.speaker_id  # 적절한 speaker_id로 교체
        self.language = server.language  # 적절한 language로 교체

    def initialize_chat(self):
        first_user_message = f"안녕하세요, 혹시 가게 영업 하나요?"
        self.add_message("user", first_user_message)
        self.add_message("assistant", self.process_script(self.first_mes))

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
        print(f"{'You' if role == 'user' else self.name}: {content}\n")
        self.manage_context_size()

    def update_world_situation(self):
        print("[현재 세계 상황]")
        for key, value in self.world_situation.items():
            print(f"{key}: {value}")

    def manage_context_size(self):
        while sum(len(msg['content']) for msg in self.conversation_history) > self.max_context_tokens and len(self.conversation_history) > 1:
            self.conversation_history.pop(0)

    def text_to_speech(self, text, model_id=0, speaker_id=0, language="JP", style="Neutral"):        
        try:
            # print(f"번역된 텍스트: {translated_text}")

            payload = {
                "text": text,
                "model_id": model_id,
                "speaker_id": speaker_id,
                "language": language,
                "style": style
            }

            response = requests.post(f"{self.TTS_SERVER_URL}/tts", json=payload)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


    def send_message_to_api(self, user_message: str):
        self.update_world_situation()
        request_data = self.prepare_api_request(user_message)

        print("\n--- API 요청 내용 ---")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        print("----------------------\n")

        response = self.make_api_request(request_data)

        if response["success"]:
            self.process_api_response(response["content"])
        else:
            print(f"Error: {response['content']}")

    def prepare_api_request(self, user_message: str) -> Dict:
        user_status = self.user_status_prompt.format(dialogue=user_message)
        self.add_message("user", user_status)

        world_status = self.format_world_status()
        char_status = self.char_status_prompt.format(likeability=self.Likeability, mental=self.Mental)

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

    def make_api_request(self, request_data: Dict) -> Dict:
        return self.claude.get_response(request_data)

    def process_api_response(self, api_response: str):
        self.add_message("assistant", self.process_script(api_response))
        likeability_match = re.search(r"Likeability: (\d+)", api_response)
        mental_match = re.search(r"Mental: (\d+)", api_response)

        if likeability_match:
            self.Likeability = int(likeability_match.group(1))
        if mental_match:
            self.Mental = int(mental_match.group(1))

        dialogue_match = re.search(r"Speaking: (.+?)(?=\n|$)", api_response, re.DOTALL)
        if dialogue_match:
            self.dialogue = dialogue_match.group(1).strip()
        else:
            self.dialogue = api_response.strip()

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

        location_match = re.search(r"Want Location: (.+?)(?=\n|$)", api_response, re.DOTALL)
        if location_match:
            self.location = location_match.group(1).strip()
        else:
            self.location = api_response.strip()

        self.translated_text = self.translator.translate(self.dialogue)

    def format_world_status(self) -> str:
        return self.world_status_prompt.format(
            time=self.world_situation["Time"],
            location=self.world_situation["Location"],
            environment=self.world_situation["Environment"],
            atmosphere=self.world_situation["Atmosphere"],
            surround_cond=self.world_situation["Surrounding Condition"]
        )

    def build_system_prompt(self):
        return self.process_script(prompt.start_prompt.replace("{{char}}", self.name)
                                   .replace("{{user}}", self.user_name).format(description=self.process_script(self.description)))

    def process_script(self, input_text: str) -> str:
        return input_text.replace("{{char}}", self.name).replace("{{user}}", self.user_name)