# FlashCard English Learning App

A web application for learning English vocabulary with flashcards and an AI-powered chatbot.

## Features

- Add new English words and get their meaning, examples, and mnemonic tips
- View and manage your flashcard history
- Delete flashcards
- Interactive chatbot for English learning support
- Chatbot can add words to flashcards via chat
- Modern UI with Bootstrap and Swiper

## How to Run

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install flask openai
   ```
3. Set your OpenAI API key in `app.py` (already set for demo)
4. Run the app:
   ```bash
   python app.py
   ```
5. Open your browser at `http://localhost:5000`

## Project Structure

```
app.py
history.json
static/
    styles.css
templates/
    index.html
    list.html
```

## Usage

- Enter an English word to add a flashcard
- Use the chatbot (bottom right) for English questions or to add words via chat
- View all flashcards in the list page

## License

MIT
