# Twitch AI Chatbot

This project implements an AI-powered Twitch chatbot using the Phi-3.5-mini-instruct model. The bot can respond to user prompts in Twitch chat, providing AI-generated responses.

## Features

- Responds to `!ai` commands in Twitch chat with AI-generated responses
- Uses the Phi-3.5-mini-instruct model for generating responses
- Provides information about the AI model with the `!aiinfo` command
- Handles long responses by splitting them into multiple messages
- Maintains conversation context for each user
- Includes logging for easier debugging and monitoring

## Prerequisites

- Python 3.9 or higher
- A Twitch account and OAuth token
- The Phi-3.5-mini-instruct-Q4_K_M.gguf model file

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/tedin7/twitch_chatbot_ai.git
   cd twitch_chatbot_ai
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   Create a `.env` file in the project root with the following content:
   ```
   TWITCH_TOKEN=your_twitch_oauth_token
   TWITCH_CHANNEL=your_twitch_channel
   BOT_NICK=your_bot_username
   BOT_TOKEN=your_bot_oauth_token
   MODEL_PATH=/path/to/your/Phi-3.5-mini-instruct-Q4_K_M.gguf
   ```

## Usage

1. Start the bot:
   ```
   python run.py
   ```

2. In your Twitch chat, you can now use the following commands:
   - `!ai <prompt>`: Generate an AI response to your prompt
   - `!aiinfo`: Display information about the AI model being used

## Configuration

You can adjust the following parameters in `llm_handler.py`:
- `n_ctx`: Context size for the model (default: 1024)
- `max_history`: Number of conversation pairs to keep in memory (default: 5)
- `max_tokens`: Maximum number of tokens in the generated response (default: 150)

## Deployment

For deployment on a server (e.g., AWS Lightsail):
1. Set up a Python environment and install dependencies as described in the Installation section.
2. Use a process manager like `systemd` to keep the bot running.
3. Consider setting up monitoring and automatic restarts.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
