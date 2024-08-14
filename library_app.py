import pymongo
import datetime

# Настройки подключения к MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")  # Подключение к серверу MongoDB на локальном хосте
db = client["library"]  # Выбор базы данных "library"
books_collection = db["books"]  # Получение ссылки на коллекцию "books"
users_collection = db["users"]  # Получение ссылки на коллекцию "users"
borrow_history_collection = db["borrow_history"]  # Получение ссылки на коллекцию "borrow_history"

# Модели (классы для представления данных)
class Book:
    """Класс для представления книги."""
    def __init__(self, title, author, genre, isbn, rating=0):
        """Инициализация объекта книги."""
        self.title = title
        self.author = author
        self.genre = genre
        self.isbn = isbn
        self.rating = rating

    def __repr__(self):
        """Возвращает строковое представление объекта книги."""
        return f"Книга: {self.title} ({self.author}) [{self.genre}]"

class User:
    """Класс для представления пользователя."""
    def __init__(self, name, email):
        """Инициализация объекта пользователя."""
        self.name = name
        self.email = email

    def __repr__(self):
        """Возвращает строковое представление объекта пользователя."""
        return f"Пользователь: {self.name} ({self.email})"

# Функции для работы с книгами
def add_book():
    """Добавляет новую книгу в базу данных."""
    title = input("Введите название книги: ")
    author = input("Введите автора книги: ")
    genre = input("Введите жанр книги: ")
    isbn = input("Введите ISBN книги: ")
    books_collection.insert_one({
        "title": title,
        "author": author,
        "genre": genre,
        "isbn": isbn,
        "rating": 0
    })
    print("Книга добавлена.")

def get_book_by_isbn():
    """Получает информацию о книге по ISBN."""
    isbn = input("Введите ISBN книги: ")
    book = books_collection.find_one({"isbn": isbn})
    if book:
        print(f"Название: {book['title']}")
        print(f"Автор: {book['author']}")
        print(f"Жанр: {book['genre']}")
        print(f"Рейтинг: {book['rating']}")
    else:
        print("Книга не найдена.")

def update_book_rating():
    """Обновляет рейтинг книги по ISBN."""
    isbn = input("Введите ISBN книги: ")
    new_rating = int(input("Введите новый рейтинг: "))
    books_collection.update_one({"isbn": isbn}, {"$set": {"rating": new_rating}})
    print("Рейтинг обновлен.")

def get_popular_books(limit=5):
    """Возвращает список самых популярных книг, отсортированных по рейтингу."""
    return list(books_collection.find().sort("rating", -1).limit(limit))

    # Функции для работы с пользователями


def add_user():
    """Добавляет нового пользователя в базу данных."""
    name = input("Введите имя пользователя: ")
    email = input("Введите email пользователя: ")
    users_collection.insert_one({"name": name, "email": email})
    print("Пользователь добавлен.")


def get_user_by_email(email):
    """Получает информацию о пользователе по email."""
    return users_collection.find_one({"email": email})

    # Функции для работы с историей выдачи книг


def record_borrow(user_email, isbn):
    """Записывает информацию о том, что пользователь взял книгу."""
    user = get_user_by_email(user_email)
    if user:
        borrow_history_collection.insert_one({
            "user_email": user_email,
            "isbn": isbn,
            "borrow_date": datetime.datetime.utcnow()
        })
        print("Книга взята.")
    else:
        print("Пользователь не найден.")


def return_book(user_email, isbn):
    """Записывает информацию о том, что пользователь вернул книгу."""
    borrow_history_collection.update_one(
        {"user_email": user_email, "isbn": isbn},
        {"$set": {"returned_date": datetime.datetime.utcnow()}}
    )
    print("Книга возвращена.")


def get_borrowed_books(user_email):
    """Возвращает список книг, взятых пользователем, но не возвращенных."""
    return list(borrow_history_collection.find({"user_email": user_email, "returned_date": None}))

    # Функция для получения рекомендаций


def recommend_books(user_email):
    """Рекомендации книг на основе предпочтений пользователя."""
    borrowed_books = get_borrowed_books(user_email)
    genres = set()
    for book in borrowed_books:
        book_data = books_collection.find_one({"isbn": book["isbn"]})
        if book_data:
            genres.add(book_data["genre"])

    if genres:
        recommendations = list(books_collection.find({"genre": {"$in": list(genres)}}).sort("rating", -1).limit(5))
        if recommendations:
            print("Рекомендации на основе ваших предпочтений:")
            for book in recommendations:
                print(f"- {book['title']} ({book['author']})")
        else:
            print("К сожалению, мы не смогли найти подходящие рекомендации.")
    else:
        print("Рекомендации на основе популярности:")
        recommendations = get_popular_books()
        for book in recommendations:
            print(f"- {book['title']} ({book['author']})")

    # Функция поиска книг по названию


def search_book_by_title():
    """Поиск книги по названию."""
    title = input("Введите название книги: ")
    books = list(books_collection.find({"title": {"$regex": title, "$options": "i"}}))
    if books:
        print("Найденные книги:")
        for book in books:
            print(f"- {book['title']} ({book['author']})")
    else:
        print("Книги не найдены.")

    # Основная функция


def main():
    """Основная функция приложения, запускающая цикл взаимодействия с пользователем."""
    while True:
        print("\nМеню:")
        print("1. Добавить книгу")
        print("2. Получить информацию о книге")
        print("3. Обновить рейтинг книги")
        print("4. Добавить пользователя")
        print("5. Взять книгу")
        print("6. Вернуть книгу")
        print("7. Получить рекомендации")
        print("8. Поиск книги по названию")
        print("9. Выход")

        choice = input("Введите номер действия: ")

        if choice == "1":
            add_book()
        elif choice == "2":
            get_book_by_isbn()
        elif choice == "3":
            update_book_rating()
        elif choice == "4":
            add_user()
        elif choice == "5":
            user_email = input("Введите email пользователя: ")
            isbn = input("Введите ISBN книги: ")
            record_borrow(user_email, isbn)
        elif choice == "6":
            user_email = input("Введите email пользователя: ")
            isbn = input("Введите ISBN книги: ")
            return_book(user_email, isbn)
        elif choice == "7":
            user_email = input("Введите email пользователя: ")
            recommend_books(user_email)
        elif choice == "8":
            search_book_by_title()
        elif choice == "9":
            break
        else:
            print("Некорректный выбор.")

# Запуск приложения
if __name__ == "__main__":
    main()
