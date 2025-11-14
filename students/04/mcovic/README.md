# Minimal scraper (Marimo) using Steel + Google Generative AI

This small project demonstrates a minimal pipeline that fetches a public webpage (via Steel if available, otherwise via `requests`), extracts the text, and sends it to Google Generative AI (Gemini) for summarization / extraction. The outputs are printed so you can copy them into a Pull Request description.

## Files
- `scraper.py` - main script (works in a Marimo notebook or as a standalone script).
- `PR_DESCRIPTION.txt` - a template / example you can paste into your PR (created by the Marimo run).

## How to run (example)
1. Install dependencies:
```bash
pip install -U beautifulsoup4 requests
# Optional (if using Steel): pip install steel-sdk
# Optional (Google client): pip install google-generativeai   # or new google-genai package
