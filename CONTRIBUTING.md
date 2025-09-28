# Contributing to Web Research Agent

We welcome contributions to the Web Research Agent! This document provides guidelines for contributing to this multi-agent research system.

## 🤝 **How to Contribute**

### **Getting Started**
1. Fork the repository
2. Clone your fork locally
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Make your changes
5. Add tests if applicable
6. Update documentation
7. Submit a pull request

### **Types of Contributions**
- **Bug fixes** - Fix existing issues
- **Feature enhancements** - Improve existing functionality
- **New features** - Add new capabilities
- **Documentation** - Improve guides and API docs
- **Tests** - Add or improve test coverage
- **Performance** - Optimize system performance

## 🏗 **Development Setup**

### **Prerequisites**
- Python 3.9+
- Node.js 16+
- MongoDB Atlas account
- API Keys: Tavily, OpenAI

### **Local Environment Setup**
```bash
# Clone your fork
git clone https://github.com/your-username/web-research-agent.git
cd web-research-agent

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
cp env.example .env  # Add your API keys
python app.py

# Frontend setup (new terminal)
cd frontend
npm install
npm start

# Database setup
# Follow the MongoDB Atlas setup guide in documentation/guides/deployment-guide.md
```

## 🧪 **Testing**

### **Running Tests**
```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests  
cd frontend && npm test

# End-to-end tests
npx playwright test
```

### **Writing Tests**
- **Backend**: Use pytest for Python tests
- **Frontend**: Use Jest and React Testing Library
- **E2E**: Use Playwright for end-to-end testing
- **Coverage**: Aim for >80% test coverage on new code

### **Test Requirements**
- All new features must include tests
- Bug fixes should include regression tests
- Tests should be clear and well-documented
- Use meaningful test names and descriptions

## 📝 **Code Style**

### **Python (Backend)**
- Follow PEP 8 style guide
- Use type hints for function signatures
- Add docstrings for all functions and classes
- Use black for code formatting: `black .`
- Use flake8 for linting: `flake8 .`

```python
# Example function with proper style
def analyze_query(query: str, options: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Analyze user query and extract search terms.
    
    Args:
        query: The user's research query
        options: Configuration options for analysis
        
    Returns:
        Dictionary containing extracted search terms
    """
    # Implementation here
    pass
```

### **TypeScript (Frontend)**
- Use ESLint and Prettier for formatting
- Follow React best practices
- Use TypeScript interfaces for props and state
- Add JSDoc comments for complex functions

```typescript
// Example component with proper style
interface ResearchFormProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export const ResearchForm: React.FC<ResearchFormProps> = ({ onSubmit, isLoading }) => {
  // Implementation here
};
```

### **General Guidelines**
- Use meaningful variable and function names
- Keep functions small and focused
- Add comments for complex logic
- Remove unused imports and variables
- Follow existing project structure

## 🔄 **Development Workflow**

### **Branch Naming**
- `feature/description` - New features
- `bugfix/description` - Bug fixes  
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### **Commit Messages**
Use conventional commit format:
```bash
type(scope): description

# Examples:
feat(backend): add query caching functionality
fix(frontend): resolve mobile responsiveness issue
docs(api): update authentication examples
test(agent): add unit tests for synthesis agent
```

### **Pull Request Process**
1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Run full test suite** locally
4. **Update CHANGELOG.md** if applicable
5. **Create detailed PR description**
6. **Request review** from maintainers

### **Pull Request Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 🏛 **Architecture Guidelines**

### **Multi-Agent System**
- Each agent should have a single, clear responsibility
- Use LangGraph state management for agent communication
- Add proper error handling and retry logic
- Document agent interactions and state transitions

### **Database Operations**
- Use async operations for all database calls
- Implement proper connection pooling
- Add indexes for query optimization
- Include data validation and sanitization

### **API Design**
- Follow RESTful API conventions
- Use appropriate HTTP status codes
- Include comprehensive error responses
- Add request/response validation

### **Frontend Components**
- Keep components small and reusable
- Use proper state management (React hooks/context)
- Implement error boundaries for robustness
- Ensure accessibility (WCAG guidelines)

## 🐛 **Bug Reports**

### **Before Reporting**
- Check existing issues for duplicates
- Test with the latest version
- Collect relevant system information

### **Bug Report Template**
```markdown
## Bug Description
Clear description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 12.0]
- Browser: [e.g., Chrome 96.0]
- Python: [e.g., 3.9.7]
- Node.js: [e.g., 16.14.0]

## Additional Context
Screenshots, logs, or other helpful information
```

## 💡 **Feature Requests**

### **Feature Request Template**
```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other approaches that were considered

## Additional Context
Any other relevant information
```

## 📋 **Code Review Guidelines**

### **For Contributors**
- Keep PRs focused and reasonably sized
- Write clear commit messages and PR descriptions
- Respond promptly to review feedback
- Test changes thoroughly before submitting

### **For Reviewers**
- Be constructive and respectful in feedback
- Check for code quality, security, and performance
- Verify tests are adequate and passing
- Ensure documentation is updated if needed

## 🌟 **Recognition**

Contributors who make significant improvements to the project will be:
- Listed in the project README
- Mentioned in release notes
- Invited to be project maintainers (for ongoing contributors)

## 📞 **Getting Help**

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the guides in `/documentation/`
- **Email**: Contact maintainers for private concerns

## 📄 **License**

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to the Web Research Agent! Every contribution helps make this multi-agent system better for everyone.** 🚀
