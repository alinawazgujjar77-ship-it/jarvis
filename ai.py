import os
import copy

from config import GEMINI_API_KEY, OPENAI_API_KEY, AUTO_WEB_SEARCH_ENABLE

try:
    from google import genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from search import SearchEngine

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


def _detect_search_intent(text: str) -> bool:
    if not text:
        return False
    t = text.lower()
    # Basic heuristic: question words or explicit search triggers
    triggers = ["who", "what", "when", "where", "why", "how", "search for", "google", "look up", "find ", "define ", "tell me about"]
    for tr in triggers:
        if tr in t:
            return True
    # If it's short command-like queries, don't auto-search
    if len(t.split()) <= 2:
        return False
    return False


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
        # Optionally perform automatic web search when intent detected
        last_user = self.history[-1]["content"] if self.history and len(self.history) > 0 else ""
        augmented_history = copy.deepcopy(self.history)

        try:
            if AUTO_WEB_SEARCH_ENABLE and _detect_search_intent(last_user):
                try:
                    se = SearchEngine()
                    results = se.search(last_user)
                    if results:
                        summary = "\n".join([f"- {r['title']}: {r['link']}" for r in results[:5]])
                        augmented_history.append({"role": "system", "content": f"Web search results:\n{summary}"})
                except Exception as e:
                    # ignore search failures and proceed
                    print("Search error while augmenting prompt:", e)

            # Prefer Gemini if available, otherwise OpenAI
            if gemini_client:
                return self._ask_gemini(augmented_history)

            if openai_client:
                return self._ask_openai(augmented_history)

            return "AI is not configured. Set OPENAI_API_KEY or GEMINI_API_KEY in config or environment."
        except Exception as exc:
            return f"AI generation error: {exc}"

    @staticmethod
    def _ask_openai(history):
        try:
            # Ensure history is in the expected format for OpenAI client
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=history,
                max_tokens=600,
                temperature=0.7,
            )
            try:
                return response.choices[0].message.content.strip()
            except Exception:
                return response.choices[0].text.strip()
        except Exception as exc:
            return f"OpenAI error: {exc}"

    @staticmethod
    def _ask_gemini(history):
        try:
            # If Gemini client expects a single prompt string, join recent messages
            # Build a prompt combining system and last user message
            # This section may need adjustments depending on genai client version
            recent = history[-6:]
            prompt_parts = []
            for m in recent:
                prompt_parts.append(f"{m['role'].upper()}: {m['content']}")
            prompt = "\n".join(prompt_parts)

            response = gemini_client.models.generate_content(
                model="gemini-1.5",
                contents=prompt
            )
            text = getattr(response, "text", None)
            if text:
                return str(text).strip()
            return str(response).strip()
        except Exception as exc:
            # If Gemini fails and OpenAI is available, fall back
            if openai_client:
                try:
                    return AIAgent._ask_openai(history)
                except Exception:
                    pass
            return f"Gemini error: {exc}"
