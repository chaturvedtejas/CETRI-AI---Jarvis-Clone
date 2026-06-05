# CETRI Architecture

This document describes the overall architecture of the CETRI AI assistant.

## High-level flow

Microphone / Keyboard Input
    ↓
Speech-to-Text (Whisper / SpeechRecognition)
    ↓
Intent & Context Engine
    ↓
LLM Brain / Response Generator
    ↓
Action Dispatcher
    ↓
System Automation / Voice Output

## Components

- `main.py`: Main application entry point and UI loop.
- `backend/`: Server-side configuration, authentication, and chat API support.
- `frontend/`: Separate web/UI component (tracked as a nested repository).
- `CETRI_AI/`: Installer artifacts and packaging utilities.

## Memory & Context

CETRI stores short-term conversation context and can be extended to persist user preferences. Example:

- User: "My favorite language is Python."
- CETRI: "Got it, I will remember that."
- Later: "What's my favorite language?"
- CETRI: "Your favorite language is Python."

## Future enhancements

- Wake-word detection ("Hey CETRI")
- Persistent memory database
- PDF/document understanding
- Desktop automation and app launcher
