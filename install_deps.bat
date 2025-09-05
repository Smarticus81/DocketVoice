@echo off
echo Installing Voice-Driven Bankruptcy Filing Assistant Dependencies...
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel

echo.
echo Installing core dependencies first...
pip install numpy scipy pandas pydantic python-dotenv requests

echo.
echo Installing pygame with pre-compiled wheel...
pip install pygame --only-binary=pygame

echo.
echo Installing AI and ML dependencies...
pip install openai anthropic langchain langchain-openai langchain-anthropic

echo.
echo Installing voice processing dependencies...
pip install SpeechRecognition elevenlabs pyaudio webrtcvad sounddevice librosa

echo.
echo Installing document processing dependencies...
pip install PyPDF2 Pillow pytesseract opencv-python pdf2image

echo.
echo Installing web and API dependencies...
pip install aiohttp fastapi uvicorn websockets

echo.
echo Installing utility dependencies...
pip install click rich tqdm colorama pydub

echo.
echo Dependencies installation complete!
echo.
echo To start the application, run: python agent.py
pause 