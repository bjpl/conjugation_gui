# Spanish Conjugation Practice GUI

A desktop application for practicing Spanish verb conjugations with AI-powered feedback using GPT-4o.

## Features

- **Interactive Practice**: Fill-in-the-blank exercises with real-world Spanish contexts
- **Multiple Modes**: Free response or multiple choice
- **AI-Powered**: GPT-4o generates exercises and provides detailed explanations
- **Customizable Practice**:
  - Select specific verb tenses (Present, Preterite, Imperfect, Future, Conditional, Subjunctive)
  - Choose grammatical persons (1st, 2nd, 3rd person singular/plural)
  - Specify verbs or themes
  - Adjust difficulty levels
- **Progress Tracking**: Track correct answers and review session summaries
- **Dark/Light Theme**: Toggle between visual themes
- **English Translations**: Optional translation display

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/conjugation_gui.git
cd conjugation_gui
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python main.py
```

## Building Executable

To create a standalone executable:

```bash
python build_exe.py
```

The executable will be created in the `dist` folder.

## Usage

1. **Configure Practice Options**:
   - Select verb tenses you want to practice
   - Choose grammatical persons
   - Optionally specify verbs or themes
   - Set difficulty level and number of exercises

2. **Generate Exercises**:
   - Click "New Exercise" to generate practice sentences

3. **Practice**:
   - Type your answer (Free Response mode) or select from options (Multiple Choice)
   - Click "Submit" to check your answer
   - Get instant AI-powered explanations
   - Use "Hint" for help
   - Navigate with Previous/Next buttons

4. **Review Progress**:
   - Click "Summary" to see session performance
   - Track correct answers in real-time

## Configuration

Settings are saved in `app_config.json` and include:
- Window size and position
- Theme preference
- API model settings
- Exercise count defaults

## Files

- `main.py` - Main application code
- `app_config.json` - User preferences
- `exercise_log.txt` - Exercise history (auto-generated)
- `session_log.txt` - Session summaries (auto-generated)
- `logging_doc.txt` - Application logs (auto-generated)

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first.