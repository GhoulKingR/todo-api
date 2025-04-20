import psycopg
import os
import hashlib

from dotenv import load_dotenv

load_dotenv()


def create_connection():
    db_url = os.environ.get("DB_URL")
    if db_url == None:
        raise ValueError("DB_URL is a required environment variable")

    return psycopg.Connection.connect(db_url)


if __name__ == "__main__":
    # Create the database tables
    conn = create_connection()
    print("Creating users db table")
    conn.execute(
        "CREATE TABLE users ("
        "   userId SERIAL PRIMARY KEY,"
        "   username VARCHAR(255) UNIQUE NOT NULL,"
        "   password VARCHAR(255) NOT NULL"
        ");"
    )
    print("Creating todoItems db table")
    conn.execute(
        "CREATE TABLE todoItems ("
        "   itemId SERIAL PRIMARY KEY,"
        "   title VARCHAR(255) NOT NULL,"
        "   description TEXT NOT NULL,"
        "   userId INT NOT NULL,"
        "   CONSTRAINT fk_user FOREIGN KEY(userId) REFERENCES users(userId)"
        ");"
    )

    # Seed users
    print("seeding users into users table")
    users = [
        ("GhoulRe", hashlib.sha256("1234".encode()).hexdigest()),
        (
            "GhoulKingR",
            hashlib.sha256("4321".encode()).hexdigest(),
        ),
        (
            "Chigozie",
            hashlib.sha256("abcba".encode()).hexdigest(),
        ),
    ]
    for user in users:
        conn.execute("INSERT INTO users (username, password) VALUES (%s, %s)", user)

    # Seed todo items
    print("Seeding todo items into todoitems table")
    todoitems = [
        ("New todo", "A new one I want to add to the list", 1),
        ("Final todo", "The final one I have to test", 1),
        ("Final todo", "The final one I have to test", 1),
        ("Write the app", "Build a fully working backend", 2),
        ("Write the app", "Build a fully working backend", 2),
        ("The new one", "Build a fully working backend", 2),
    ]
    for item in todoitems:
        conn.execute(
            "INSERT INTO todoitems (title, description, userId) VALUES (%s, %s, %s)",
            item,
        )

    conn.commit()
    conn.close()
    print("All done ✨")
