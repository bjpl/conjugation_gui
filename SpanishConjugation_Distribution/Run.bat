@echo off
echo Starting Spanish Conjugation Practice...
echo.
if not exist .env (
    echo Please create a .env file with your OpenAI API key.
    echo See .env.example for the format.
    echo.
    pause
    exit
)
SpanishConjugation.exe
