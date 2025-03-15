# KokoAI RSS Summarizer

## Overview
This script fetches RSS feeds, summarizes the content using an AI model from Ollama, and sends the summarized articles to a Slack channel. It only fetches news from the current day.

## Requirements
- Python 3
- Required Python packages (install with `pip install -r requirements.txt`):
  - `requests`
  - `lxml`
  - `ollama`
  - `slack_sdk`
- [Ollama](https://ollama.com) installed and running
- An RSS feed list stored in `feeds.txt`
- A Slack API token

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/matandomuertos/KokoAI-RSS-Summarizer.git
   cd KokoAI-RSS-Summarizer
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
Set the following environment variables:

- `SLACK_API_TOKEN` – Your Slack API token.
- `OLLAMA_HOST` – URL of the Ollama server (default: `http://localhost:11434`).
- `MODEL` – AI model name (default: `llama3.2`).
- `SYSTEM_OPS` – AI system instructions. Example:
  ```bash
  export SYSTEM_OPS="You are an AI summarizer. Summarize blog posts in 5 lines or fewer, keeping key points and relevant details. Avoid unnecessary information."
  ```

## Usage
1. Add RSS feed URLs to `feeds.txt` (one per line).
2. Run the script:
   ```bash
   python main.py
   ```

## How It Works
1. Reads RSS feed URLs from `feeds.txt`.
2. Fetches and parses the RSS feed.
3. Filters articles published today.
4. Summarizes content using Ollama AI.
5. Sends the summary to a Slack channel.

## Troubleshooting
- **No messages in Slack?** Check if `SLACK_API_TOKEN` is set.
- **AI not responding?** Ensure Ollama is running and accessible at `OLLAMA_HOST`.
- **Feeds not loading?** Verify `feeds.txt` contains valid URLs.

## License
Apache License 2.0
