# Python Voice Assistant

An AI-powered desktop voice assistant developed using Python.

## Features

- Modern graphical interface using CustomTkinter
- Voice input through microphone
- Text-to-speech voice responses
- AI-powered conversations using Ollama
- Open Mac applications using voice commands
- Date and time information
- Local conversation memory

## Technologies Used

- Python
- CustomTkinter
- SpeechRecognition
- PyAudio
- pyttsx3
- Ollama
- Requests
- python-dotenv

## Project Setup

### 1. Clone the repository

```bash
git clone https://github.com/devbhatt0239-sudo/OIBSIP.git
cd OIBSIP
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Download Ollama from https://ollama.com

Pull the AI model:

```bash
ollama pull qwen2.5:3b
```

### 5. Configure environment

Copy `.env.example` to `.env` and update the required settings, if applicable.

### 6. Run the project

```bash
python main.py
```

## Example Commands

- Hello
- How are you?
- What is the time?
- What is today's date?
- Open Safari
- Open VS Code
- Ask me anything

## Learning Outcomes

This project demonstrates Python programming, GUI development, speech recognition, text-to-speech, AI integration, and application automation.

## Developer

**Dev Bhatt**

B.Tech Computer Science Engineering

Oasis Infobyte - Python Programming

## Internship

Oasis Infobyte – Python Programming Internship