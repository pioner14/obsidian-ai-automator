# Obsidian AI Automator

## Project Overview

This project provides an automated workflow to transcribe video files, analyze their content using a local Large Language Model (LLM) via Ollama, and generate structured Markdown notes for Obsidian. It's designed to help researchers quickly extract key insights and examples from lectures or other spoken content.

The workflow consists of a Bash wrapper script that orchestrates audio extraction, transcription, and LLM-driven analysis, ultimately saving the processed information into an Obsidian vault.

## Technologies Used

*   **Bash:** For the main automation wrapper script.
*   **FFmpeg:** For extracting audio from video files.
*   **Whisper.cpp (CUDA version):** For high-performance audio transcription, specifically using the `large-v3` model for Russian language.
*   **Python:** For interacting with the Ollama API, processing transcripts, and formatting output for Obsidian.
*   **`requests` (Python library):** For making HTTP requests to the Ollama server.
*   **Ollama:** A local LLM serving platform used for semantic analysis of transcripts.
*   **Obsidian:** The target note-taking application where the generated Markdown files are stored.

## Building and Running

### Prerequisites

Before running the project, ensure you have the following installed and configured:

1.  **FFmpeg:**
    ```bash
    # Example for Arch Linux (adjust for your distribution)
    sudo pacman -S ffmpeg
    ```
2.  **Whisper.cpp (CUDA version) and `large-v3` model:**
    ```bash
    # Example for Arch Linux using paru (AUR helper)
    paru -S whisper.cpp-cuda whisper.cpp-model-large-v3
    ```
    Ensure `WHISPER_CMD` in `obsidian-ai-transcribe.sh` points to the correct executable (e.g., `/usr/bin/whisper.cpp-cuda`) and `WHISPER_MODEL_PATH` points to the `ggml-large-v3.bin` model (e.g., `/usr/share/whisper-cpp/models/ggml-large-v3.bin`).
3.  **Ollama:**
    Install Ollama from [ollama.com](https://ollama.com/).
    Pull the desired model (e.g., `phi3:mini`):
    ```bash
    ollama pull phi3:mini
    ```
    Ensure `OLLAMA_MODEL` in `scripts/ai_analyzer.py` matches the model you pulled.
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
    This Python script handles reading Whisper transcripts, sending them to Ollama for analysis, and formatting the output as Obsidian Markdown notes.
3.  **Create `obsidian-ai-transcribe.sh`:**
    (Already done)
    This Bash script is the main entry point, coordinating audio extraction, transcription, and calling the Python analyzer.

### Running the Workflow

1.  **Start Ollama Server (if not already running):**
    ```bash
    ollama serve &
    ```
    This command runs Ollama in the background. You only need to do this once after a system reboot.
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
