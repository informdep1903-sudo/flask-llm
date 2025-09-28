# Основной файл приложения Flask

# Импортируем необходимые компоненты:
    # Flask - основной класс для создания веб-приложения
    # render_template - функция для рендеринга HTML шаблонов
    # request - объект для работы с HTTP-запросами
    # jsonify - функция для создания JSON-ответов
from flask import Flask, render_template, request, jsonify
    # Импортируем компоненты для работы с базой данных и чатом
from models import db, ChatHistory, chat_with_llm

# Создаем экземпляр Flask-приложения
app = Flask(__name__)
# Настраиваем подключение к SQLite базе данных
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
# Инициализируем объект базы данных с нашим приложением
db.init_app(app)

# Маршрут для главной страницы
@app.route("/")
def home():
    # Получаем всю историю чата из базы данных, отсортированную по времени
    chat_history = ChatHistory.query.order_by(ChatHistory.timestamp.asc()).all()
    # Формируем HTML-страницу на основе шаблона index.html и передаем в него историю чата
    return render_template("index.html", chat_history=chat_history)

# Маршрут для обработки сообщений чата (только POST-запросы)
@app.route("/chat", methods=["POST"])
def chat():
    # Получаем JSON-данные из запроса
    data = request.get_json()
    # Извлекаем сообщение пользователя
    user_message = data.get("message", "")

    # Получаем ответ от модели ИИ
    llm_reply = chat_with_llm(user_message)
    # Создаем новую запись в истории чата
    new_entry = ChatHistory(user_message=user_message, llm_reply=llm_reply)
    # Добавляем и сохраняем запись в базе данных
    db.session.add(new_entry)
    db.session.commit()
    # Возвращаем ответ в формате JSON
    return jsonify({"reply": llm_reply})

# Запускаем приложение только если файл запущен напрямую
if __name__ == "__main__":
    # Создаем все необходимые таблицы в базе данных
    with app.app_context():
        db.create_all()
    # Запускаем приложение в режиме отладки
    app.run(debug=True)