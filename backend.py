import snowflake.connector
from config import SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA, SNOWFLAKE_WAREHOUSE

# Function to establish connection to Snowflake
def get_connection():
    return snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
    )

# Function to register a new user
def register_user(name, email, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Check if user already exists
        cur.execute("SELECT * FROM users WHERE email = %s;", (email,))
        if cur.fetchone():
            return "❌ User already exists! Try logging in."

        # Insert new user
        cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'user');",
                    (name, email, password))
        conn.commit()
        return "✅ Registration successful! Please log in."
    
    except Exception as e:
        return f"❌ Registration failed: {str(e)}"
    
    finally:
        cur.close()
        conn.close()

# Function to authenticate user
def login_user(email, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT user_id, role FROM users WHERE email = %s AND password = %s;", (email, password))
        user = cur.fetchone()
        if user:
            return {"user_id": user[0], "role": user[1]}
        return None  # Invalid login

    except Exception as e:
        return None

    finally:
        cur.close()
        conn.close()



def login_admin(email, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT admin_id FROM admin WHERE email = %s AND password = %s;", (email, password))
        admin = cur.fetchone()
        if admin:
            return {"admin_id": admin[0]}
        return None  # Invalid login

    except Exception as e:
        return None

    finally:
        cur.close()
        conn.close()


# Function to fetch all available books
def get_books():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT book_id, title, author, genre, year FROM books WHERE available = TRUE;")
        books = cur.fetchall()
        return books

    except Exception as e:
        return []

    finally:
        cur.close()
        conn.close()

# Function to borrow a book
def borrow_book(user_id, book_id):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Check if book is available
        cur.execute("SELECT available, title FROM books WHERE book_id = %s;", (book_id,))
        book = cur.fetchone()
        if not book or not book[0]:
            return "❌ Book is already borrowed!"

        # Get user name from users table
        cur.execute("SELECT name FROM users WHERE user_id = %s;", (user_id,))
        user_name = cur.fetchone()[0]

        # Mark book as borrowed (not available)
        cur.execute("UPDATE books SET available = FALSE WHERE book_id = %s;", (book_id,))

        # Add transaction entry
        cur.execute("INSERT INTO transactions (user_id, book_id, borrow_date) VALUES (%s, %s, CURRENT_TIMESTAMP);",
                    (user_id, book_id))

        # Insert into borrowed_books_history
        cur.execute("""
            INSERT INTO borrowed_books_history (user_id, user_name, book_id, book_title, issued_date)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP);
        """, (user_id, user_name, book_id, book[1]))  # book[1] is the book title

        conn.commit()

        return "✅ Book borrowed successfully!"
    
    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return f"❌ Borrowing failed: {str(e)}"
    
    finally:
        cur.close()
        conn.close()


# Function to return a book
def return_book(transaction_id, book_id):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Mark book as available again
        cur.execute("UPDATE books SET available = TRUE WHERE book_id = %s;", (book_id,))

        # Get the user_id and book title for the transaction
        cur.execute("""
            SELECT u.user_id, u.name, b.title 
            FROM transactions t
            JOIN users u ON t.user_id = u.user_id
            JOIN books b ON t.book_id = b.book_id
            WHERE t.transaction_id = %s;
        """, (transaction_id,))
        user_data = cur.fetchone()

        if not user_data:
            return "❌ Transaction not found."

        user_id, user_name, book_title = user_data

        # Get the current date for return
        return_date = "CURRENT_DATE"  # You can use CURRENT_TIMESTAMP if you want a timestamp

        # Insert the return details into borrowed_books_history table
        cur.execute("""
            UPDATE borrowed_books_history 
            SET return_date = CURRENT_DATE
            WHERE user_id = %s AND book_id = %s AND return_date IS NULL;
        """, (user_id, book_id))  # Mark the return date for the book

        # Remove the transaction entry (optional)
        cur.execute("DELETE FROM transactions WHERE transaction_id = %s;", (transaction_id,))

        conn.commit()

        return "✅ Book returned successfully!"
    
    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return f"❌ Error returning book: {str(e)}"

    finally:
        cur.close()
        conn.close()

# Function to fetch borrowed books for admin
def get_borrowed_books():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT t.transaction_id, u.name, b.title, t.borrow_date, b.book_id
            FROM transactions t
            JOIN users u ON t.user_id = u.user_id
            JOIN books b ON t.book_id = b.book_id;
        """)
        borrowed_books = cur.fetchall()
        return borrowed_books

    except Exception as e:
        return []

    finally:
        cur.close()
        conn.close()

def get_all_users():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT user_id, name, email FROM users;")
        users = cur.fetchall()
        return users  # Returns a list of tuples (user_id, name, email)

    except Exception as e:
        return []

    finally:
        cur.close()
        conn.close()


# Function to search books
def search_books(query):
    conn = get_connection()
    cursor = conn.cursor()

    search_query = """
    SELECT book_id, title, author, genre, year, available 
    FROM books 
    WHERE title ILIKE %s OR author ILIKE %s OR genre ILIKE %s
    """
    cursor.execute(search_query, ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results