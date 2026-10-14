# Social Media Content Generator

A simple Python application for generating social media captions and hashtag suggestions using prompt-based logic.

## Features
- Accepts a topic, product, or content idea
- Supports multiple platform selection
- Offers tone and caption-length choices
- Generates multiple content variations
- Creates hashtags and supports emoji preferences
- Includes download and regeneration flows
- Validates required inputs and shows friendly errors
- Uses OpenAI when OPENAI_API_KEY is configured, with a built-in fallback otherwise

## Project Structure
- app.py - Main Streamlit application
- requirements.txt - Python dependencies
- tests/ - Automated tests

## Installation
```bash
cd "Project 22 - Social Media Content generator"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the App
```bash
streamlit run app.py
```

## Testing
```bash
pytest -q
```
