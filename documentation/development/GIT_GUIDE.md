# Git Usage Guide - cognitive-core

## Repository Configuration

This repository has specific Git configuration to avoid conflicts in shared development environments.

### Current Setup
- **Repository Name:** cognitive-core
- **Remote Origin:** https://github.com/Samrat2803/cognitive-core.git
- **Author:** Samrat Sah <samrat.sah28@gmail.com> (repository-specific)

## Important Notes

### 🔧 Repository-Specific Git Config
This repo uses **local** git configuration (not global) to avoid conflicts with other users on the same machine:

```bash
# Current settings (already configured)
git config user.name "Samrat Sah"
git config user.email "samrat.sah28@gmail.com"
```

### 📁 Clean Repository
- All build artifacts are properly ignored via `.gitignore`
- `node_modules/`, `__pycache__/`, `test-results/`, etc. are excluded
- Only source code and configuration files are tracked

## Daily Git Workflow

### Basic Commands
```bash
# Check status
git status

# Add changes
git add .
# Or add specific files
git add path/to/file

# Commit changes
git commit -m "Your descriptive commit message"

# Push to GitHub
git push

# Pull latest changes
git pull
```

### Branch Management
```bash
# Create new feature branch
git checkout -b feature/your-feature-name

# Switch branches
git checkout main
git checkout feature/your-feature-name

# Merge feature branch
git checkout main
git merge feature/your-feature-name

# Delete feature branch
git branch -d feature/your-feature-name
```

## Before You Start Developing

### 1. Verify Git Config
```bash
# Check your local config for this repo
git config --get user.name
git config --get user.email
```

### 2. Pull Latest Changes
```bash
git pull origin main
```

### 3. Install Dependencies
```bash
# Backend
cd backend && source .venv/bin/activate && uv pip install -r requirements.txt

# Frontend  
cd frontend && npm install
```

## Repository Maintenance

### Keep It Clean
- Never commit `node_modules/` or `__pycache__/`
- Always check `git status` before committing
- Use descriptive commit messages
- Keep commits focused and atomic

### File Structure
```
cognitive-core/
├── .gitignore          # Comprehensive ignore rules
├── GIT_GUIDE.md        # This file
├── README.md           # Main project documentation
├── backend/            # Python FastAPI backend
├── frontend/           # React TypeScript frontend
├── tests/              # Test suites
├── scripts/            # Utility scripts
└── documentation/      # Additional docs
```

## Troubleshooting

### Wrong Author in Commits?
```bash
# Set correct author for this repo only
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Fix last commit author
git commit --amend --reset-author --no-edit
```

### Need to Reset Local Config?
```bash
# Check current settings
git config --list --local

# Remove local config (will use global settings)
git config --unset user.name
git config --unset user.email
```

---

**Repository:** https://github.com/Samrat2803/cognitive-core  
**Last Updated:** September 2025
