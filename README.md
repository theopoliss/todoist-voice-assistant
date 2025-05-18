# Todoist Voice Assistant

A voice-powered AI assistant that helps you manage your Todoist tasks through natural language conversations. Speak commands to create, find, update, and delete tasks in your Todoist account.

## Features

- **Voice-Controlled**: Speak naturally to manage your tasks
- **Natural Language Understanding**: Powered by GPT models to understand complex requests
- **Contextual Awareness**: Maintains conversation history for multi-turn interactions
- **Task Management**:
  - Create tasks with content, due dates, and priorities
  - Find existing tasks using keyword search
  - Update task details
  - Delete tasks

## Requirements

- Python 3.9+
- Microphone for voice input
- OpenAI API key
- Todoist API token

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/todoist-assistant.git
   cd todoist-assistant
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install SpeechRecognition PyAudio openai pydantic-settings todoist-api-python
   ```

## Configuration

1. Create a `.env` file in the project root with the following variables:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   TODOIST_API_TOKEN=your_todoist_api_token_here
   MODEL=gpt-4o-mini  # Or another OpenAI model you prefer
   ```

   To get these API keys:

   - **OpenAI API Key**: Get it from [OpenAI Platform](https://platform.openai.com/api-keys)
   - **Todoist API Token**: Get it from Todoist Settings → Integrations → Developer → API token

## Usage

1. Make sure your virtual environment is active:

   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Run the assistant:

   ```bash
   python -m app.main
   ```

3. When the assistant starts, you'll see "Voice Assistant Activated. Say 'exit' or 'quit' to stop." followed by "Listening... Say your command:".

4. Speak your command clearly. Example commands:
   - "Create a task to buy groceries tomorrow at 5pm"
   - "Remind me to call John on Friday"
   - "Find tasks about meeting"
   - "Update the grocery task to be due on Saturday"
   - "Delete the task about calling John"
   - Say "exit" to quit the assistant

## Project Structure

- `app/main.py`: The entry point with voice recognition and the main loop
- `app/llm_tools.py`: LLM integration and tool definitions for task management
- `app/todoist_client.py`: Wrapper functions for Todoist API
- `app/config.py`: Configuration management using pydantic-settings

## How It Works

1. The assistant listens for your voice command using the SpeechRecognition library
2. Your speech is converted to text and sent to an OpenAI LLM
3. The LLM interprets the command and decides what action to take
4. For task-related actions, the LLM calls the appropriate Todoist API function
5. The result is spoken back to you
6. The conversation history is maintained for context across multiple commands

## Troubleshooting

- **Microphone issues**: Ensure your microphone is working and that you've granted permission to use it.
- **"Could not find PyAudio"**: If on macOS, install PortAudio first with `brew install portaudio`
- **API errors**: Verify your API keys in the `.env` file are correct
- **Voice recognition issues**: Speak clearly and in a quiet environment

## License

[MIT License](LICENSE)
