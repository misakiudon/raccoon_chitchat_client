import requests
from IPython.display import Audio, display
import io
import src.module as module

# 서버 URL을 여기에 입력하세요 (Ngrok URL)
TTS_SERVER_URL = "https://a631-157-82-13-201.ngrok-free.app"  # 실제 Ngrok URL로 교체해야 합니다
model_id = 0
speaker_id = 0
language = "JP"

def text_to_speech(text, model_id=0, speaker_id=0, language="JP", style="Neutral"):
    """
    텍스트를 음성으로 변환하는 함수

    :param text: 변환할 텍스트
    :param model_id: 사용할 모델 ID (기본값: 0)
    :param speaker_id: 화자 ID (기본값: 0)
    :param language: 언어 (기본값: "JP" for Japanese)
    :return: 오디오 객체 또는 None (오류 발생 시)
    """
    payload = {
        "text": text,
        "model_id": model_id,
        "speaker_id": speaker_id,
        "language": language,
        "style": style
    }

    try:
        response = requests.post(f"{TTS_SERVER_URL}/tts", json=payload)
        if response.status_code == 200:
            audio_data = io.BytesIO(response.content)
            return Audio(audio_data.read(), autoplay=True)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
