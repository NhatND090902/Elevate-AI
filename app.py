from flask import Flask, render_template, request, redirect, url_for
import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


# Load config from .env
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")

# Khởi tạo OpenAI client
client = openai.OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

HISTORY_FILE = "history.json"


# Hàm lưu kết quả vào file JSON
def save_to_history(word, result):
    history_data = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history_data = json.load(f)
            except json.JSONDecodeError:
                pass

    history_data.append({"word": word, "result": result})

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)


# Hàm lấy danh sách flashcard
def get_history():
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                pass
    return history


# Hàm xóa flashcard
def delete_flashcard(index):
    history_data = get_history()
    if 0 <= index < len(history_data):
        del history_data[index]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)


# Hàm gọi API và trả về kết quả
def explain_word(word):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful English vocabulary tutor. "
                "When given an English word, you provide:\n"
                "1. Its meaning in Vietnamese\n"
                "2. Two example sentences in English\n"
                "3. A memorable tip or mnemonic to help learn the word."
            ),
        },
        {"role": "user", "content": "Analyze the English word: 'resilient'"},
        {
            "role": "assistant",
            "content": (
                "1. Nghĩa: Kiên cường, có khả năng phục hồi nhanh sau khó khăn\n\n"
                "2. Ví dụ:\n"
                "- She is a resilient woman who always bounces back from failure.\n"
                "- The city was resilient after the earthquake.\n\n"
                "3. Mẹo học dễ nhớ:\n"
                'Tưởng tượng từ "resilient" giống như cao su — bị bóp méo nhưng luôn trở lại hình dạng cũ.'
            ),
        },
        {"role": "user", "content": f"Analyze the English word: '{word}'"},
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    return response.choices[0].message.content


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    word = None
    if request.method == "POST":
        word = request.form["word"]
        result = explain_word(word)
        save_to_history(word, result)

    history = get_history()
    history = history[::-1]  # Đảo ngược để mới nhất ở đầu

    return render_template("index.html", result=result, word=word, history=history)


@app.route("/list")
def flashcard_list():
    """Hiển thị danh sách tất cả flashcard"""
    history = get_history()
    history = history[::-1]  # Đảo ngược để mới nhất ở đầu
    return render_template("list.html", history=history)


@app.route("/delete/<int:index>")
def delete_flashcard_route(index):
    """Xóa flashcard theo index"""
    history = get_history()
    # Chuyển đổi index vì list được đảo ngược khi hiển thị
    actual_index = len(history) - 1 - index
    delete_flashcard(actual_index)
    return redirect(url_for("flashcard_list"))


function_tools = [
    {
        "type": "function",
        "function": {
            "name": "add_word_to_flashcard",
            "description": "Thêm từ tiếng Anh vào danh sách học (flashcard)",
            "parameters": {
                "type": "object",
                "properties": {
                    "word": {
                        "type": "string",
                        "description": "Từ tiếng Anh cần thêm vào danh sách",
                    }
                },
                "required": ["word"],
            },
        },
    }
]


# Chatbot route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    messages = [
        {
            "role": "system",
            "content": (
                "You are a friendly and multilingual chatbot that helps users learn English. "
                "You can understand and respond in the user's language, such as Vietnamese, English, and others.\n\n"
                "Your main goals are:\n"
                "1. Help users learn English vocabulary, grammar, and provide example sentences and tips.\n"
                "2. Allow casual and friendly conversation (e.g. 'How are you?', 'Hôm nay bạn thế nào?').\n"
                "3. If the user asks about a topic unrelated to English learning or casual talk, politely respond:\n"
                "   'I'm here to help with English learning topics. Could you please ask something related to vocabulary, grammar, or learning tips?'\n"
                "4. If the user writes something in English with grammar mistakes, kindly point out the mistakes, explain them briefly, and continue the conversation naturally.\n\n"
                "Always detect and respond in the same language the user uses."
            ),
        },
        {"role": "user", "content": "How are you today?"},
        {
            "role": "assistant",
            "content": "I'm doing great, thank you! How can I help you learn English today?",
        },
        {"role": "user", "content": "I very like this word."},
        {
            "role": "assistant",
            "content": (
                "I think you meant: 'I really like this word.' — 'Very' is not used this way in this context. "
                "Keep practicing, you're doing well!"
            ),
        },
        {"role": "user", "content": "What's the weather like?"},
        {
            "role": "assistant",
            "content": (
                "I'm here to help with English learning topics. Could you please ask something related "
                "to vocabulary, grammar, or learning tips?"
            ),
        },
        {"role": "user", "content": "Bạn khỏe không?"},
        {
            "role": "assistant",
            "content": "Mình khỏe, cảm ơn bạn! Bạn muốn học gì hôm nay về tiếng Anh?",
        },
        {"role": "user", "content": user_message},
    ]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=function_tools,
        tool_choice="auto",
    )
    choice = response.choices[0]
    reply = choice.message.content or ""

    if choice.finish_reason == "tool_calls":
        tool_call = choice.message.tool_calls[0]
        function_args = json.loads(tool_call.function.arguments)
        word = function_args.get("word")

        if word:
            explanation = explain_word(word)
            save_to_history(word, explanation)
            reply = f"✅ Đã thêm từ '{word}' vào flashcard."
        else:
            reply = "Không tìm thấy từ để thêm."
    else:
        reply = choice.message.content or "Xin lỗi, tôi không hiểu bạn."
    return {"reply": reply}


if __name__ == "__main__":
    app.run(debug=True)
