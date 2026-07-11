from voice import speak, listen
from ai import AIAgent
from config import ASSISTANT_NAME, USER_NAME
from memory.memory import MemoryManager

def main():
    agent = AIAgent()
    memory = MemoryManager()
    speak(f"Hello {USER_NAME}. I am {ASSISTANT_NAME}.")

    while True:
        command = listen()
        if not command:
            continue
        memory.remember("last_command" ,command)

        normalized = command.strip().lower()
        if normalized in {"exit", "quit", "goodbye", "stop"}:
            speak(f"Goodbye {USER_NAME}.")
            break

        reply = agent.ask(command)
        memory.remember("last_reply" , reply)
        print(f"{ASSISTANT_NAME}: {reply}")
        speak(reply)


if __name__ == "__main__":
    main()
