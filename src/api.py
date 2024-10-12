from openai import OpenAI

class GPT4OpenAI:
    def __init__(self):
        self.model = "gpt-4o"  # OpenAI model name
        self.api_key = ""  # Replace with your actual OpenAI API key
        self.client = OpenAI(api_key=self.api_key)

    def get_response(self, arg):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=arg["messages"],
                max_tokens=arg.get("max_tokens", 1024),
                temperature=arg.get("temperature", 1.0),
                top_p=arg.get("top_p", 1.0)
            )
            return {
                "success": True,
                "content": response.choices[0].message.content
            }
        except Exception as e:
            return {
                "success": False,
                "content": str(e)
            }
