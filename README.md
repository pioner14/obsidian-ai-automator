# Obsidian AI Automator

## Project Overview

This project provides an automated workflow to transcribe video files using Deepgram, analyze their content using NVIDIA Large Language Models (LLM) via NVIDIA API, and generate structured Markdown notes for Obsidian. It's designed to help researchers quickly extract key insights and examples from lectures or other spoken content.

The workflow consists of a Bash wrapper script that orchestrates audio extraction, transcription, and LLM-driven analysis, ultimately saving the processed information into an Obsidian vault.

## Technologies Used

*   **Bash:** For the main automation wrapper script.
*   **FFmpeg:** For extracting audio from video files.
*   **Python:** For interacting with Deepgram and NVIDIA APIs, processing transcripts, and formatting output for Obsidian.
*   **`requests` (Python library):** For making HTTP requests to Deepgram and NVIDIA servers.
*   **Deepgram:** For high-performance audio/video transcription.
*   **NVIDIA API:** For accessing NVIDIA Large Language Models for semantic analysis of transcripts.
*   **Obsidian:** The target note-taking application where the generated Markdown files are stored.

## Building and Running

### Prerequisites

Before running the project, ensure you have the following installed and configured:

1.  **FFmpeg:**
    ```bash
    # Example for Arch Linux (adjust for your distribution)
    sudo pacman -S ffmpeg
    ```
2.  **Deepgram API Key:**
    Obtain a Deepgram API key from [deepgram.com](https://deepgram.com/). Set it as an environment variable:
    ```bash
    export DEEPGRAM_API_KEY="YOUR_DEEPGRAM_API_KEY"
    ```
3.  **NVIDIA API Key:**
    Obtain an NVIDIA API key from [nvidia.com](https://www.nvidia.com/developer/ai-foundation-models/). Set it as an environment variable:
    ```bash
    export NVIDIA_API_KEY="YOUR_NVIDIA_API_KEY"
    ```
4.  **Python 3 and `requests` library:**
    ```bash
    pip install requests
    ```
5.  **Obsidian Vault:**
    Ensure `OBSIDIAN_VAULT_PATH` in `scripts/ai_analyzer.py` is correctly set to the desired directory within your Obsidian vault where notes should be saved (e.g., `/home/nick/Obsidian_Vault/Auto_Notes`).

### Setup

1.  **Initialize Git Repository:**
    (Already done)
    ```bash
    cd /home/nick/Projects/obsidian-ai-automator
    git init
    echo "# Obsidian AI Automator" > README.md
    echo "*.mp3" >> .gitignore
    echo "*.wav" >> .gitignore
    echo "*.json" >> .gitignore
    echo "Очистка от больших медиа и временных файлов" >> .gitignore
    git add .
    git commit -m "Initial commit: Setup project structure and .gitignore"
    mkdir scripts
    ```
2.  **Create `scripts/ai_analyzer.py`:**
    (Already done)
    This Python script handles Deepgram transcription, sending transcripts to NVIDIA API for analysis, and formatting the output as Obsidian Markdown notes.
3.  **Create `obsidian-ai-transcribe.sh`:**
    (Already done)
    This Bash script is the main entry point, coordinating audio extraction, transcription, and calling the Python analyzer.

### Running the Workflow

1.  **Set API Keys:**
    Ensure your `DEEPGRAM_API_KEY` and `NVIDIA_API_KEY` environment variables are set before running the script.
    ```bash
    export DEEPGRAM_API_KEY="YOUR_DEEPGRAM_API_KEY"
    export NVIDIA_API_KEY="YOUR_NVIDIA_API_KEY"
    ```
2.  **Execute the main script:**
    Navigate to the project root directory:
    ```bash
    cd /home/nick/Projects/obsidian-ai-automator
    ```
    Run the script with the path to your video file:
    ```bash
    ./obsidian-ai-transcribe.sh /path/to/your/video.mp4
    ```

## Development Conventions

*   **Git Usage:** The project uses Git for version control. Commits should have clear, descriptive messages.
*   **Script Structure:** Bash scripts are used for orchestration, while Python handles more complex logic and API interactions.
*   **Configuration:** Key paths and model names are defined as variables at the top of the scripts for easy modification.
*   **Temporary Files:** Intermediate audio and JSON transcript files are stored in `/tmp` and cleaned up after processing.
*   **Obsidian Integration:** Generated Markdown files include YAML frontmatter and Obsidian callouts for structured note-taking.