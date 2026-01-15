# Jobaru - Local AI Job Application Agent

Jobaru is a fully autonomous, local AI agent that helps you apply to jobs. It runs entirely on your machine using [Ollama](https://ollama.com/), keeping your data private.

## Features
- 📄 **Resume Parsing**: Extracts text from PDF or Text resumes.
- 🧠 **Smart Matching**: Analyzes job descriptions against your resume using local LLMs.
- ✍️ **Auto-Drafting**: Generates tailored cover letters and application emails.
- 🔒 **Privacy First**: No data leaves your machine.

## Prerequisites
1.  **Python 3.8+**
2.  **Ollama** installed and running.
    - [Download Ollama](https://ollama.com/download)
    - Pull a model: `ollama pull llama3` (or `mistral`, `gemma`, etc.)

## Installation

1.  Clone this repository (if applicable) or download the source.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Prepare your Resume
Save your resume as `resume.pdf` or `resume.txt` in the project folder.

### 2. Run the Agent
You can pass a job description file or a raw string.

**Using a Job Description File:**
```bash
python main.py --resume resume.pdf --job job_desc.txt
```

**Specifying a Model:**
```bash
python main.py --resume resume.pdf --job job_desc.txt --model mistral
```

### 3. Review Output
Results are saved in the `applications/` folder, organized by timestamp.
- `cover_letter.md`: Ready-to-send cover letter.
- `email_draft.txt`: Draft for email application.
- `data.json`: Full analysis including match score and missing skills.

## Project Structure
- `main.py`: Entry point.
- `src/`: Core logic modules.
- `applications/`: Generated outputs.
