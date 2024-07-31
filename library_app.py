import pymongo
import datetime

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["library"]
books_collection = db["books"]
users_collection = db["users"]
borrow_history_collection = db["borrow_history"]

class Book:
    def __init__(self, title, author, genre, isbn, rating=0):
        self.title = title
        self.author = author
        self.genre = genre
        self.isbn = isbn
        self.rating = rating

    def __repr__(self):
        return f"Книга: {self.title} ({self.author}) [{self.genre}]"

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return f"Пользователь: {self.name} ({self.email})"

def add_book():
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
    isbn = input("Введите ISBN книги: ")
    book = books_collection.find_one({"isbn": isbn})
    if book:
        print(f"Название: {book['title']}")
        print(f"Автор: {book['author']}")
        print(f"Жанр: {book['genre']}")
        print(f"Рейтинг: {book['rating']}")
    else:
        print("Книга не найдена.")

def update_book_rating(isbn):
    book = get_book_by_isbn(isbn)
    if book:
        rating = int(input("Введите новый рейтинг: "))
        books_collection.update_one({"isbn": isbn}, {"$set": {"rating": rating}})
        print("Рейтинг обновлен.")
    else:
        print("Книга не найдена.")

def get_popular_books(limit=5):
    return list(books_collection.find().sort("rating", -1).limit(limit))

def add_user():
    name = input("Введите имя пользователя: ")
    email = input("Введите email пользователя: ")
    users_collection.insert_one({"name": name, "email": email})
    print("Пользователь добавлен.")

def get_user_by_email(email):
    return users_collection.find_one({"email": email})

def record_borrow(user_email, isbn):
    borrow_history_collection.insert_one({
        "user_email": user_email,
        "isbn": isbn,
        "borrow_date": datetime.datetime.utcnow()
    })
    print("Книга взята.")


def get_user_borrow_history(user_email):
    return list(borrow_history_collection.find({"user_email": user_email}))


def analyze_user_preferences(user_email):
    borrow_history = get_user_borrow_history(user_email)
    genre_counts = {}
    for borrow in borrow_history:
        book = books_collection.find_one({"isbn": borrow["isbn"]})
        if book:
            genre = book["genre"]
            if genre in genre_counts:
                genre_counts[genre] += 1
            else:
                genre_counts[genre] = 1

    if genre_counts:
        most_popular_genre = max(genre_counts, key=genre_counts.get)
        return most_popular_genre
    else:
        return None


def recommend_books(user_email):
    preferred_genre = analyze_user_preferences(user_email)
    if preferred_genre:
        recommendations = list(books_collection.find(
            {"genre": preferred_genre}
        ).sort("rating", -1).limit(3))
        print("Рекомендованные книги:")
        for book in recommendations:
            print(f"- {book['title']} ({book['author']})")
    else:
        print("Рекомендации на основе популярности:")
        popular_books = get_popular_books()
        for book in popular_books:
            print(f"- {book['title']} ({book['author']})")


def main():
    while True:
        print("nМеню:")
        print("1. Добавить книгу")
        print("2. Получить информацию о книге")
        print("3. Обновить рейтинг книги")
        print("4. Добавить пользователя")
        print("5. Взять книгу")
        print("6. Получить рекомендации")
        print("7. Выход")

        choice = input("Введите номер действия: ")

        if choice == "1":
            add_book()
        elif choice == "2":
            get_book_by_isbn()
        elif choice == "3":
            isbn = input("Введите ISBN книги: ")
            update_book_rating(isbn)
        elif choice == "4":
            add_user()
        elif choice == "5":
            user_email = input("Введите email пользователя: ")
            isbn = input("Введите ISBN книги: ")
            record_borrow(user_email, isbn)
        elif choice == "6":
            user_email = input("Введите email пользователя: ")
            recommend_books(user_email)
        elif choice == "7":
            break
        else:
            print("Некорректный выбор.")


if __name__ == "__main__":
    main()