import os

from config import GEMINI_API_KEY, OPENAI_API_KEY

try:
    from google import genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

openai_client = None
if OpenAI and OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print("OpenAI client init error:", e)
        openai_client = None

gemini_client = None
if genai and GEMINI_API_KEY:
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print("Gemini client init error:", e)
        gemini_client = None

class AIAgent:
    def __init__(self):
        self.history = [
            {
                "role": "system",
                "content": "You are Jarvis, a helpful digital assistant for Fizan. Keep responses clear, polite, and useful."
            }
        ]

    def ask(self, prompt):
        if not prompt or not prompt.strip():
            return "Please say something so I can help."

        self.history.append({"role": "user", "content": prompt.strip()})
        response_text = self._generate_response()
        self.history.append({"role": "assistant", "content": response_text})
        return response_text

    def _generate_response(self):
        # Prefer OpenAI if available, otherwise try Gemini
        if openai_client:
            return self._ask_openai(self.history)

        if gemini_client:
            return self._ask_gemini(self.history[-1]["content"])

        return "AI is not configured. Set OPENAI_API_KEY or GEMINI_API_KEY in config or environment."

    @staticmethod
    def _ask_openai(history):
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=history,
                max_tokens=600,
                temperature=0.7,
            )
            # response shape can vary between versions; try both common access patterns
            try:
                return response.choices[0].message.content.strip()
            except Exception:
                return response.choices[0].text.strip()
        except Exception as exc:
            return f"OpenAI error: {exc}"

    @staticmethod
    def _ask_gemini(prompt):
        try:
            # Use a more common model name (gemini-1.5) and simpler prompt body
            response = gemini_client.models.generate_content(
                model="gemini-1.5",
                contents=f"""
you are Jarvis, an AI assistant.
Rules:
- Reply in 1 to 3 short sentences.
- Maximum 30 words.
- Do not use Markdown.
- Do not use bullet points.
- Speak naturally like Jarvis.
User: {prompt}
"""
            )
            # response may expose .text or another attribute depending on the client version
            text = getattr(response, "text", None)
            if text:
                return str(text).strip()
            return str(response).strip()
        except Exception as exc:
            return f"Gemini error: {exc}"
