# Contributing to Crawl4AI Web Application

Thank you for your interest in contributing to the Crawl4AI Web Application! We welcome contributions from the community and are grateful for your support.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Git
- Basic knowledge of FastAPI, HTML/CSS/JavaScript

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/crawl4ai-web.git
   cd crawl4ai-web
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   playwright install-deps  # Linux only
   ```

4. **Set up environment**
   ```bash
   cp .env.example .env
   ```

5. **Run the application**
   ```bash
   python run.py --reload
   ```

## 🤝 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/your-username/crawl4ai-web/issues)
2. If not, create a new issue with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Screenshots if applicable

### Suggesting Features

1. Check [Issues](https://github.com/your-username/crawl4ai-web/issues) for existing feature requests
2. Create a new issue with:
   - Clear description of the feature
   - Use case and benefits
   - Possible implementation approach

### Code Contributions

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run the application
   python run.py
   
   # Test manually in browser
   # Add automated tests if applicable
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: your descriptive commit message"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## 📝 Coding Standards

### Python Code Style

- Follow [PEP 8](https://pep8.org/) guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Use type hints where appropriate

### Frontend Code Style

- Use consistent indentation (2 spaces for HTML/CSS/JS)
- Follow semantic HTML practices
- Use Bootstrap classes consistently
- Comment complex JavaScript logic
- Optimize for mobile responsiveness

### Commit Message Format

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(api): add new extraction strategy endpoint
fix(ui): resolve mobile layout issues
docs(readme): update installation instructions
```

## 🧪 Testing

### Manual Testing

1. Test basic crawling functionality
2. Test different extraction strategies
3. Test error handling
4. Test responsive design on different devices
5. Test API endpoints using the docs interface

### Adding Tests

- Add unit tests for new functions
- Add integration tests for API endpoints
- Test edge cases and error conditions
- Ensure tests are independent and repeatable

## 📚 Documentation

### Code Documentation

- Add docstrings to all functions and classes
- Include parameter types and return values
- Provide usage examples for complex functions

### User Documentation

- Update README.md for new features
- Add examples and screenshots
- Update API documentation
- Keep installation instructions current

## 🔍 Code Review Process

1. **Automated Checks**: PRs must pass all automated checks
2. **Manual Review**: Core maintainers will review code for:
   - Functionality and correctness
   - Code quality and style
   - Documentation completeness
   - Test coverage
3. **Feedback**: Address review comments promptly
4. **Approval**: At least one maintainer approval required

## 🏗️ Project Structure

```
crawl4ai-web/
├── app/                    # Main application
│   ├── api/               # API routes
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── static/                # Frontend assets
├── templates/             # HTML templates
├── tests/                 # Test files (if added)
└── docs/                  # Documentation (if added)
```

## 🚀 Release Process

1. **Version Bumping**: Update version in relevant files
2. **Changelog**: Update CHANGELOG.md with new features/fixes
3. **Testing**: Ensure all tests pass
4. **Tagging**: Create git tag for release
5. **Documentation**: Update documentation as needed

## 💬 Communication

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact maintainers for security issues

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to Crawl4AI Web Application! 🎉
