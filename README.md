# Spanish Conjugation Practice GUI

A desktop application for practicing Spanish verb conjugations with both offline and AI-powered modes.

## Features

### Core Learning Features
- **Dual Mode Operation**: 
  - **Offline Mode**: Local conjugation engine with 100+ verbs (no internet required)
  - **Online Mode**: GPT-4o powered for contextual exercises and explanations
- **Smart Progress Tracking**: SQLite database tracks all attempts with spaced repetition
- **Adaptive Review**: Automatically identifies and practices weak areas
- **Verb Classification**: Handles regular, irregular, and stem-changing verbs

### Practice Options
- **Interactive Exercises**: Fill-in-the-blank with real Spanish contexts
- **Multiple Modes**: Free response or multiple choice
- **Customizable Practice**:
  - All major tenses (Present, Preterite, Imperfect, Future, Conditional, Subjunctive)
  - All grammatical persons (yo, tú, él/ella, nosotros, vosotros, ellos)
  - Specify verbs or themes
  - Three difficulty levels (Beginner, Intermediate, Advanced)

### Learning Tools
- **Spaced Repetition**: Optimized review scheduling based on performance
- **Mistake Review**: Dedicated mode for practicing problematic verbs
- **Progress Statistics**: Track accuracy, learning curves, and weak areas
- **Session Summaries**: Review performance after each session

### UI Features
- **Dark/Light Theme**: Toggle between visual themes
- **English Translations**: Optional translation display
- **Progress Bar**: Visual feedback on exercise completion

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