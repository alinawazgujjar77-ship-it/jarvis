from voice import speak, listen
from ai import AIAgent
from config import ASSISTANT_NAME, USER_NAME, WAKE_WORD, ENABLE_WAKE_WORD, MEMORY_MAX_ITEMS, MEMORY_TTL_DAYS
from memory.memory import MemoryManager


def main():
    agent = AIAgent()
    memory = MemoryManager()

    # Load previous conversations and greet
    convs = memory.get_conversations(limit=10)
    speak(f"Hello {USER_NAME}. I am {ASSISTANT_NAME}.")
    if ENABLE_WAKE_WORD and WAKE_WORD:
        speak(f"Say '{WAKE_WORD}' to wake me up.")

    while True:
        command = listen()
        if not command:
            continue

        cmd_clean = command.strip()
        lower = cmd_clean.lower()

        # Wake word handling
        if ENABLE_WAKE_WORD and WAKE_WORD:
            if WAKE_WORD.lower() not in lower:
                # Not a wake command; ignore
                continue
            # Remove wake word from text
            # Only remove the first occurrence
            idx = lower.find(WAKE_WORD.lower())
            cmd_clean = (cmd_clean[:idx] + cmd_clean[idx + len(WAKE_WORD):]).strip()
            if not cmd_clean:
                # If user only said wake word, prompt
                speak("Yes?")
                continue

        memory.append_conversation("user", cmd_clean)
        memory.remember("last_command", cmd_clean)

        normalized = cmd_clean.strip().lower()
        if normalized in {"exit", "quit", "goodbye", "stop"}:
            speak(f"Goodbye {USER_NAME}.")
            memory.append_conversation("assistant", f"Goodbye {USER_NAME}.")
            break

        reply = agent.ask(cmd_clean)
        memory.remember("last_reply", reply)
        memory.append_conversation("assistant", reply)

        print(f"{ASSISTANT_NAME}: {reply}")
        speak(reply)

        # Periodic pruning
        memory.prune_conversations(max_items=MEMORY_MAX_ITEMS, ttl_days=MEMORY_TTL_DAYS)


if __name__ == "__main__":
    main()
