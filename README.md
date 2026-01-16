# Jobaru 🤖💼

**A Human-Controlled, Privacy-First AI Job Application Agent**

Jobaru is a local-first AI agent that helps you discover, evaluate, and apply to jobs with minimal effort — while keeping you in control at every critical step.

It runs entirely on your machine using Ollama (local LLMs) to analyze your resume, identify suitable roles, draft tailored applications, and assist with job submissions — without sending your personal data to third-party AI services.

**Jobaru is designed to assist, not impersonate.**

## ✨ What Jobaru Actually Does

Jobaru turns job hunting into a supervised automation pipeline:

*   Reads your real resume
*   Infers roles that fit your profile
*   Searches for recent openings
*   Drafts role-specific application content
*   Assists with form filling
*   Stops and asks you before anything irreversible

**You remain the decision-maker. Jobaru handles the boring parts.**

## 🚀 Features

*   **Resume Intelligence**: Analyzes your resume locally to infer suitable roles and skill alignment.
*   **Smart Job Discovery**: Finds recent job listings and filters duplicates to reduce noise.
*   **Assisted Apply (Not Blind Automation)**: Can help fill “Easy Apply” forms using only your provided data.
*   **Human-in-the-Loop by Design**: Pauses for:
    *   Final review & submission
    *   Custom questions
    *   Ambiguous or subjective fields
*   **Privacy-First Architecture**:
    *   Runs fully on your machine
    *   Uses local LLMs via Ollama
    *   Your resume and analysis never leave your system
    *   No cloud AI APIs

## 🔐 Control & Safety Model

Jobaru is intentionally not a fire-and-forget bot.

*   You log in manually
*   You review generated content
*   You approve submissions
*   You can run in draft-only / dry-run mode
*   You can stop it at any time

**Think of Jobaru as a power assistant, not an impersonator.**

## 🛠️ Prerequisites

*   **Python 3.10+**
*   **Google Chrome**
*   **Ollama** (local LLM runtime)
    *   Download from [ollama.com](https://ollama.com)
    *   Example model: `ollama pull mistral`

## 📦 Installation

```bash
git clone https://github.com/Sly-kitsune/jobaru-llm-job-agent.git
cd jobaru-llm-job-agent
pip install -r requirements.txt
```

## 🏃 Usage

1.  **Prepare your resume**
    *   `resume.pdf` or `resume.txt`

2.  **Run Jobaru**
    ```bash
    python main.py
    ```

3.  **Follow the guided flow**
    *   Optional resume analysis
    *   Role suggestions
    *   Job discovery
    *   Draft generation

4.  **Manual login**
    *   A browser opens
    *   You log in yourself

5.  **Supervise & approve**
    *   Review before submit
    *   Edit anything you want
    *   Jobaru proceeds only when allowed

## ⚠️ Responsible Use Notice

Jobaru is a personal productivity tool.

*   It does not bypass authentication
*   It does not scrape private data
*   It does not falsify credentials
*   It acts only on user-provided information
*   **Users are responsible for complying with the terms of platforms they interact with**

*This project is intended for educational, personal, and experimental use.*

## 🧠 Why This Exists

Job hunting is repetitive, time-consuming, and mentally draining.

Jobaru exists because:
> “I didn’t want to keep doing dumb manual work — so I automated it.”

## 🤝 Contributing

PRs, issues, and forks are welcome.
If you care about agent systems, automation, and local-first AI, you’ll feel at home here.
