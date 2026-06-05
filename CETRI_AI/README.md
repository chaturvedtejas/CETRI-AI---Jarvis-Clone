# CETRI AI Assistant

**CETRI** (Cognitive Enhanced Technical Response Intelligence) is an advanced AI assistant inspired by Jarvis from Iron Man. This Python-based implementation provides voice interaction, automation tools, and an intuitive GUI dashboard.

## Core Features

- **Voice Interaction**: Speech-to-text (Whisper) and text-to-speech (pyttsx3)
- **Intelligent Responses**: Calm, composed, and slightly witty personality
- **Automation**: OS control and file handling capabilities
- **GUI Dashboard**: Simple, clean interface built with tkinter
- **Command Processing**: Understands natural language commands

## Installation

### Option 1: One-Click Installer (Recommended)

1. Download the project files
2. Run install.bat as administrator
3. CETRI will be installed to %USERPROFILE%\CETRI_AI\
4. Shortcuts created on Desktop and Start Menu

### Option 2: Manual Installation

1. **Prerequisites:**
   - Python 3.8+ (download from python.org)
   - Windows 10/11

2. **Install Dependencies:**
   `ash
   pip install -r requirements.txt
   `

3. **Run CETRI:**
   `ash
   python main.py
   `

### Option 3: Standalone Executable

Use the pre-built CETRI_AI_Assistant.exe in the dist folder:
- No Python installation required
- All dependencies bundled
- Ready to run on any Windows PC

## System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space (includes Whisper models)
- **Microphone**: Optional (for voice input)
- **Speakers/Headphones**: Required (for voice output)

## Usage

### First Launch
- First run downloads Whisper AI models (~140MB)
- May take 1-2 minutes on first startup

### Commands
- hello / hi - Greeting
- 	ime - Current time
- create file - Create new file
- open file - Open file explorer
- help - List commands
- quit - Exit CETRI

### Voice Mode (Optional)
1. Install PyAudio: pip install pyaudio
2. Restart CETRI
3. Press Enter for voice input

## Architecture

- **main.py**: Core CETRI application
- **requirements.txt**: Python dependencies
- **cetri.spec**: PyInstaller configuration
- **install.bat**: Windows installer script
- **CETRI_AI_Assistant.exe**: Standalone executable

## Personality

CETRI operates with:
- Accuracy and practical solutions
- Efficiency and intelligent suggestions
- Calm, composed demeanor with subtle wit
- Proactive problem-solving mindset

## Troubleshooting

### Common Issues

**'Python not found'**
- Install Python from python.org
- Add Python to PATH during installation

**'Whisper model download failed'**
- Check internet connection
- Restart CETRI (models cache locally)

**'Microphone not working'**
- Install PyAudio: pip install pyaudio
- Check microphone permissions in Windows

**'Tkinter GUI not working'**
- Use console version (works on all systems)
- Reinstall Python with tcl/tk support

### Performance Tips

- Close other applications during first run
- Ensure stable internet for model download
- Use SSD for faster loading

## Development

### Project Structure
`
CETRI_AI/
+-- main.py                 # Main application
+-- requirements.txt        # Dependencies
+-- cetri.spec             # PyInstaller config
+-- install.bat            # Installer script
+-- README.md              # This file
+-- dist/                  # Built executables
+-- .github/               # Documentation
`

### Building from Source

1. **Setup Environment:**
   `ash
   git clone <repository>
   cd cetri-ai
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   `

2. **Run Development Version:**
   `ash
   python main.py
   `

3. **Build Executable:**
   `ash
   pip install pyinstaller
   pyinstaller cetri.spec
   `

## License

This project is open-source. See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch
3. Submit pull request

## Support

For issues or questions:
- Check troubleshooting section
- Create GitHub issue
- Review console output for error messages

---

*Inspired by Jarvis from Iron Man — your intelligent personal assistant.*
