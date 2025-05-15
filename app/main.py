import speech_recognition as sr
import asyncio
from app.llm_tools import handle_user
# If config is needed directly in main.py, uncomment:
# from .config import settings

def listen_and_get_text() -> str | None:
    """Listens to microphone input and returns the recognized text."""
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening... Say your command:")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            print("No speech detected within the time limit.")
            return None

    print("Recognizing speech...")
    try:
        text = recognizer.recognize_google(audio) # Uses Google Web Speech API by default
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Google Web Speech API could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during speech recognition: {e}")
        return None

async def voice_assistant_loop():
    """Main loop for the voice assistant, maintaining conversation history."""
    print("Voice Assistant Activated. Say 'exit' or 'quit' to stop.")
    
    conversation_history: list[dict] = [
        {"role": "system", "content": "You are a helpful voice assistant for managing Todoist tasks. If you need to ask for clarification, be concise."}
    ]

    while True:
        user_input_text = listen_and_get_text()

        if user_input_text:
            if user_input_text.lower() in ["exit", "quit", "stop"]:
                print("Exiting voice assistant.")
                break

            print(f"Processing: '{user_input_text}'...")
            assistant_response_text, updated_history = await handle_user(user_input_text, conversation_history)
            
            conversation_history = updated_history 
            
            print(f"Assistant: {assistant_response_text}")
        else:
            print("No valid input received. Try again or say 'exit'.")
        print("-" * 20) # Separator

if __name__ == "__main__":
    # This is the entry point to start the assistant
    # Ensure you have an event loop running if other parts of your app need it
    # For a simple script like this, asyncio.run() is fine.
    try:
        asyncio.run(voice_assistant_loop())
    except KeyboardInterrupt:
        print("\nAssistant interrupted. Exiting.")
    except Exception as e:
        print(f"An unexpected error occurred in the main loop: {e}")