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

## Downloading the Phi-3.5 Mini Model

To use this chatbot, you need to download the Phi-3.5-mini-instruct-Q4_K_M.gguf model. Follow these steps:

1. Install the Hugging Face CLI if you haven't already:
   ```
   pip install huggingface_hub
   ```

2. Login to Hugging Face (you may need to create an account if you don't have one):
   ```
   huggingface-cli login
   ```

3. Download the model:
   ```
   huggingface-cli download microsoft/Phi-3.5-mini-instruct-GGUF Phi-3.5-mini-instruct-Q4_K_M.gguf --local-dir . --local-dir-use-symlinks False
   ```

4. Once downloaded, update the `MODEL_PATH` in your `.env` file to point to the location of the downloaded .gguf file.

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

## Connecting to Multiple Channels

This bot now supports easy connection to multiple Twitch channels using a web interface. To use this feature:

1. Set up a Twitch Developer Application and note down the Client ID and Client Secret
2. Add the Client ID and Client Secret to your `.env` file
3. Run the bot using `python run.py`
4. Open a web browser and go to `http://localhost:5000`
5. Click on "Connect to Twitch" and authorize the application
6. The bot will automatically join your channel

Note: Make sure you have the necessary OAuth tokens and permissions to join the channels you add.
