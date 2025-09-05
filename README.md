# 🎤 Voice-Driven Bankruptcy Filing Assistant

A **conversational AI bankruptcy attorney** that guides users through the entire bankruptcy filing process using natural voice interaction.

## 🚀 Features

- **🎤 Fully Voice-Driven**: Complete bankruptcy filing through natural conversation
- **🤖 AI-Powered**: Specialized bankruptcy law LLM with legal reasoning and guardrails
- **📄 Document Analysis**: AI analyzes uploaded documents (PDFs, images, text) for relevant information
- **📋 Complete Forms**: Generates all required federal bankruptcy forms and schedules
- **🧮 Means Test**: Automatic Chapter 7 vs Chapter 13 eligibility calculation
- **🔒 Legal Guardrails**: Built-in legal disclaimers and safety measures
- **📱 User-Friendly**: Conversational interface that feels like talking to a friendly attorney

## 🏗️ Architecture

### Voice Pipeline
- **TTS**: ElevenLabs with fallback to system TTS
- **STT**: Google Speech Recognition with Pocketsphinx fallback
- **Audio**: Pygame for cross-platform audio handling

### AI Pipeline
- **Primary Model**: GPT-4o for reasoning and vision
- **Fallback**: GPT-4-turbo for complex legal analysis
- **Specialized**: Bankruptcy law expertise with legal context and guardrails

## 📁 Project Structure

```
rando/
├── agent.py                 # Main voice-driven application
├── voice_utils.py          # Voice interaction utilities
├── bankruptcy_llm.py       # Specialized bankruptcy AI
├── means_test.py           # Bankruptcy means test calculator
├── pdf_generator.py        # Federal form PDF generator
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── documents/             # Upload documents here for AI analysis
└── venv/                  # Python virtual environment
```

## 🛠️ Installation

### Windows (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rando
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Install dependencies (Choose one method):**
   
   **Option A: Double-click `install_deps.bat`** (Easiest)
   
   **Option B: Run PowerShell script**
   ```powershell
   .\install_deps.ps1
   ```
   
   **Option C: Manual installation**
   ```bash
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the template and fill in your keys:
   copy env_template.txt .env
   
   # Edit .env file with your actual API keys:
   OPENAI_API_KEY=your_openai_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   ELEVENLABS_VOICE_ID=your_preferred_voice
   ```

### Mac/Linux

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rando
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (same as Windows)

## 🎯 Usage

### Start the Application

**Windows (Recommended):**
- **Double-click `start.bat`** - This handles everything automatically

**Manual Start:**
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Run the application
python agent.py
```

### Test Interruptable Voice System

Test the pause/resume functionality:
```bash
python test_interrupt.py
```

This demonstrates:
- Press Ctrl+C to pause
- Say "pause" to pause
- Say "continue" to resume
- Say "quit" to exit
- Check status with "status"

### Voice Commands
- **"help"** - Show available voice commands
- **"go back"** - Return to previous step
- **"skip"** - Skip current section
- **"review"** - Review collected information
- **"start over"** - Restart the process
- **"exit"** - Exit application

#### Interruptable Commands
- **"pause"** or **"stop"** - Pause the application
- **"continue"** or **"resume"** - Resume after pause
- **"status"** - Show current progress and operation
- **Ctrl+C** - Keyboard shortcut to pause (anytime)

### Document Upload
1. Place documents in the `documents/` folder
2. Supported formats: PDF, JPG, PNG, TXT
3. Say "analyze documents" to begin AI analysis

## 📋 What Gets Generated

### Complete Bankruptcy Package
- **Form 101**: Voluntary Petition
- **Schedule A/B**: Real and Personal Property
- **Schedule C**: Exemptions
- **Schedule D**: Secured Creditors
- **Schedule E/F**: Unsecured Creditors
- **Schedule I**: Monthly Income
- **Schedule J**: Monthly Expenses
- **Form 122A**: Means Test Calculation
- **Form 107**: Statement of Financial Affairs

### Output Files
- `complete_bankruptcy_data.json` - All collected information
- `bankruptcy_petition.pdf` - Complete federal forms ready for court

## 🔒 Legal Disclaimers

- **NOT LEGAL ADVICE**: This application provides educational information only
- **CONSULT ATTORNEY**: Always consult with a qualified bankruptcy attorney
- **NO GUARANTEES**: No guarantee of bankruptcy eligibility or discharge
- **INFORMATIONAL ONLY**: For bankruptcy filing preparation purposes

## 🎤 Voice Experience

The AI acts as a **friendly bankruptcy attorney** who:
- Asks questions in natural, conversational language
- Explains bankruptcy concepts in plain English
- Guides users through each step of the process
- Validates information and offers corrections
- Generates complete, court-ready documentation

### 🎯 Interruptable Voice System
- **Pause/Resume**: Say "pause" or press Ctrl+C to pause at any time
- **Voice Commands**: "continue", "resume", "quit", "exit", "help"
- **Graceful Interruption**: Long operations can be paused and resumed
- **Status Updates**: Check current progress with "status" command
- **Context Preservation**: All data is preserved during pauses

## 🚨 Requirements

- **Python 3.8+**
- **Microphone** for voice input
- **Speakers/Headphones** for voice output
- **Internet connection** for AI services
- **API keys** for OpenAI and ElevenLabs

## 🔧 Troubleshooting

### Pygame Installation Issues (Windows)
If you get pygame compilation errors:
1. **Use the provided scripts**: `install_deps.bat` or `install_deps.ps1`
2. **Force wheel installation**: `pip install pygame --only-binary=pygame`
3. **Alternative**: `pip install pygame --pre --find-links https://github.com/pygame/pygame/releases`

**Note**: The pygame warning about `pkg_resources` is harmless and can be ignored. It's a deprecation warning that doesn't affect functionality.

### Voice Issues
- Check microphone permissions
- Ensure speakers are working
- Verify API keys are set correctly

### AI Analysis Issues
- Check OpenAI API key
- Ensure documents are in supported formats
- Verify internet connection

### Dependency Issues
- Ensure you're using Python 3.8+
- Try upgrading pip: `python -m pip install --upgrade pip`
- Use virtual environment: `python -m venv venv`

### Missing API Keys
- **OpenAI API Key**: Required for AI document analysis. Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **ElevenLabs API Key**: Required for voice synthesis. Get from [ElevenLabs](https://elevenlabs.io/)
- **Without API Keys**: Application runs with limited features (manual data entry only)
- **Setup**: Copy `env_template.txt` to `.env` and fill in your keys

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure environment variables are set correctly

## 📄 License

This project is for educational purposes. Bankruptcy filing should be done under the guidance of qualified legal professionals.

---

**Remember**: This is not legal advice. Always consult with a qualified bankruptcy attorney before filing. 