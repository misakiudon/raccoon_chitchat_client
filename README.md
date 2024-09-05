# raccoon_chitchat_client
Client for llm-tts server.

# How to use
Worked in python version 3.9 and 3.10. 

## Install

```sh
git clone https://github.com/misakiudon/raccoon_chitchat_client.git
cd raccoon_chitchat_client
python -m venv venv
source venv/bin/activate #Linux
# venv\Scripts\activate # Windows
pip install -r requirements.txt
```

## Run
```sh
ngrok authtoken {your_ngrok_authtoken}
python client.py -u https://server-ngrok-url.ngrok-free.app -k {your_openai_api_key}
```

