# Contributing to Spanish Conjugation Practice App

Thank you for your interest in contributing! We welcome contributions from the community.

## How to Contribute

### Reporting Issues

Before creating an issue, please check if it already exists. When creating a new issue, include:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)
- Error messages or screenshots

### Suggesting Features

Open an issue with the `enhancement` label and describe:

- The problem your feature solves
- How you envision it working
- Any implementation ideas

### Code Contributions

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/conjugation_gui.git
   cd conjugation_gui
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set Up Development Environment**
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Mac/Linux: source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Make Your Changes**
   - Follow existing code style
   - Add docstrings to functions
   - Update README if needed
   - Test your changes thoroughly

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Describe your changes

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 120 characters
- Use descriptive variable names

### Commit Messages

Format: `<type>: <description>`

Types:
- `Add`: New feature
- `Fix`: Bug fix
- `Update`: Enhancement to existing feature
- `Refactor`: Code restructuring
- `Docs`: Documentation changes
- `Test`: Test additions/changes

### Testing

Before submitting:
1. Test offline mode functionality
2. Test with API key (online mode)
3. Verify UI responsiveness
4. Check for console errors
5. Test on different screen sizes

### Adding New Features

When adding features:
1. Discuss in an issue first
2. Keep backwards compatibility
3. Update documentation
4. Add configuration options if needed
5. Consider offline mode compatibility

## Project Structure

```
conjugation_gui/
├── main.py                 # Main GUI application
├── conjugation_engine.py   # Core conjugation logic
├── exercise_generator.py   # Exercise generation
├── progress_tracker.py     # Database and tracking
├── task_scenarios.py       # Task-based exercises
├── speed_practice.py       # Speed mode
└── learning_path.py        # Learning progression
```

### Key Areas for Contribution

- **New Verbs**: Add more irregular verbs to `conjugation_engine.py`
- **Exercise Templates**: Expand templates in `exercise_generator.py`
- **UI Improvements**: Enhance PyQt5 interface in `main.py`
- **Learning Algorithms**: Improve spaced repetition in `progress_tracker.py`
- **Localization**: Add support for more languages
- **Performance**: Optimize database queries and UI rendering

## Pull Request Process

1. **Update Documentation**: Include any necessary documentation changes
2. **Test Coverage**: Ensure your code is tested
3. **Clean Code**: Remove debug prints and commented code
4. **One Feature Per PR**: Keep PRs focused on a single feature/fix
5. **Respond to Feedback**: Be responsive to review comments

## Code Review Criteria

PRs will be reviewed for:
- Code quality and style
- Test coverage
- Documentation
- Performance impact
- User experience
- Backwards compatibility

## Community Guidelines

### Be Respectful
- Treat everyone with respect
- Welcome newcomers
- Be patient with questions

### Be Constructive
- Provide helpful feedback
- Explain your reasoning
- Suggest improvements

### Be Collaborative
- Work together toward solutions
- Share knowledge
- Help others learn

## Getting Help

- Check existing issues and discussions
- Join our [Discord server](https://discord.gg/spanish-learning) (if available)
- Ask questions in GitHub Discussions
- Tag maintainers for urgent issues

## Recognition

Contributors will be:
- Listed in the README
- Mentioned in release notes
- Given credit in commit messages

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue with the `question` label or reach out to the maintainers.

Thank you for helping make this project better! 🎉