.PHONY: help install dev test lint format run run-cli run-voice clean

help:
	@echo "JARVIS Pro - Development Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Install dev dependencies"
	@echo ""
	@echo "Running:"
	@echo "  make run          - Run GUI mode"
	@echo "  make run-cli      - Run CLI mode"
	@echo "  make run-voice    - Run voice mode"
	@echo ""
	@echo "Development:"
	@echo "  make test         - Run unit tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Check code quality"
	@echo "  make format       - Format code"
	@echo "  make type-check   - Type checking"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Clean up cache/temp files"
	@echo "  make reset-db     - Reset memory database"

# Installation
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Done!"

dev: install
	@echo "Installing dev dependencies..."
	pip install black flake8 mypy pytest pytest-cov
	@echo "Done!"

# Running
run:
	@python main.py

run-cli:
	@python main.py --cli

run-voice:
	@python main.py --voice

run-debug:
	@python main.py --debug

# Testing
test:
	@echo "Running tests..."
	pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=core --cov=vision --cov=automation --cov=gui --cov=plugins --cov=utils

# Code Quality
lint:
	@echo "Linting code..."
	flake8 . --exclude=venv,__pycache__
	@echo "Done!"

format:
	@echo "Formatting code..."
	black .
	@echo "Done!"

type-check:
	@echo "Type checking..."
	mypy . --ignore-missing-imports
	@echo "Done!"

# Maintenance
clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov/
	@echo "Done!"

reset-db:
	@echo "Resetting database..."
	rm -f data/jarvis.db
	@echo "Done! Database will be recreated on next run."

setup: install
	@echo "Setting up project..."
	cp .env.example .env
	@echo "Created .env file. Please edit with your API keys."
	@echo "Then run: make run"
