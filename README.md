# Discord Music Bot

This is a simple Discord bot that can join a voice channel and play music from YouTube. It uses `discord.py` for interaction with the Discord API and `yt-dlp` for downloading and streaming YouTube videos.

## Features

- Join and leave voice channels
- Play, pause, resume, and stop music from YouTube

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed Python 3.8 or higher.
- You have a Discord account and a bot token. You can create a bot and get the token from the [Discord Developer Portal](https://discord.com/developers/applications).
- You have installed `ffmpeg` and added it to your system PATH. You can download it from the [FFmpeg website](https://ffmpeg.org/download.html).

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/PgNetwork01/discord-music-bot.git
    cd discord-music-bot
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the project directory and add your bot token:

    ```env
    DISCORD_BOT_TOKEN=your-bot-token
    ```

## Usage

Run the bot using the following command:

```bash
python bot.py
