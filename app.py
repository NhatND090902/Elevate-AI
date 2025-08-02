from flask import Flask, render_template, request, redirect, url_for
import openai
import json
import os

app = Flask(__name__)

# Khởi tạo OpenAI client
client = openai.OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key="sk-uZCEwpnpSDlzc1iARlWvwQ",
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
        model="GPT-4o-mini",
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
    return redirect(url_for('flashcard_list'))


if __name__ == "__main__":
    app.run(debug=True)
