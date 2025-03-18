import streamlit as st
import pandas as pd
from backend import (
    register_user, search_books, login_user, login_admin,
    get_books, borrow_book, get_borrowed_books, return_book, get_all_users
)

st.set_page_config(page_title="Library Management", layout="wide")

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_id = None

# Sidebar Authentication
st.sidebar.title("🔐 Authentication")
auth_choice = st.sidebar.radio("Select Role", ["User Login", "Admin Login", "Register User"])

# User Registration
if auth_choice == "Register User":
    st.sidebar.subheader("User Registration")
    new_name = st.sidebar.text_input("Full Name")
    new_email = st.sidebar.text_input("Email")
    new_password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Register"):
        msg = register_user(new_name, new_email, new_password)
        st.sidebar.success(msg)

# User Login
elif auth_choice == "User Login":
    st.sidebar.subheader("User Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        user_info = login_user(email, password)
        if user_info:
            st.session_state.logged_in = True
            st.session_state.user_id = user_info["user_id"]
            st.session_state.user_role = "user"
            st.sidebar.success(f"✅ Logged in as User ({email})")
        else:
            st.sidebar.error("❌ Invalid email or password!")

# Admin Login
elif auth_choice == "Admin Login":
    st.sidebar.subheader("Admin Login")
    email = st.sidebar.text_input("Admin Email")
    password = st.sidebar.text_input("Admin Password", type="password")

    if st.sidebar.button("Login"):
        admin_info = login_admin(email, password)
        if admin_info:
            st.session_state.logged_in = True
            st.session_state.user_id = admin_info["admin_id"]
            st.session_state.user_role = "admin"
            st.sidebar.success(f"✅ Logged in as Admin ({email})")
        else:
            st.sidebar.error("❌ Invalid admin credentials!")

# Main Application Logic
if st.session_state.logged_in:
    st.title("📚 Library Management System")

    # Admin Panel
    if st.session_state.user_role == "admin":
        st.subheader("📌 Admin Panel")

        # ✅ Creating two columns for Registered Users & Borrowed Books
        col1, col2 = st.columns(2)

        # 📌 Left Column: Registered Users
        with col1:
            st.subheader("👥 Registered Users")
            users = get_all_users()  # Fetch all users

            if users:
                df_users = pd.DataFrame(users, columns=["User ID", "Name", "Email"])
                st.dataframe(df_users, height=500)  # Adjust height as needed
            else:
                st.info("No users registered yet.")

        # 📌 Right Column: Borrowed Books
        with col2:
            st.subheader("📖 Borrowed Books")
            borrowed_books = get_borrowed_books()

            if borrowed_books:
                for i, transaction in enumerate(borrowed_books):
                    transaction_id, user_name, book_title, borrow_date, book_id = transaction
                    st.write(f"📖 **{book_title}** borrowed by **{user_name}** on {borrow_date}")
                    
                    # Ensure each button has a unique key
                    unique_key = f"return_{transaction_id}_{i}"

                    if st.button(f"Return '{book_title}'", key=unique_key):
                        msg = return_book(transaction_id, book_id)
                        st.success(msg)
                        st.rerun()
            else:
                st.info("No books are currently borrowed.")

    else:
        # User Panel
        search_term = st.text_input("🔍 Search for a book by title, author, or genre:")
        if search_term:
            books = search_books(search_term)
            if books:
                df = pd.DataFrame(books, columns=["Book ID", "Title", "Author", "Genre", "Year", "Available"])
                st.dataframe(df)
            else:
                st.warning("No books found!")

        st.subheader("📖 Borrow a Book")
        books = get_books()
        for book in books:
            book_id, title, author, genre, year = book
            st.write(f"**{title}** by {author} ({year}) - *{genre}*")
            
            if st.button(f"Borrow '{title}'", key=f"borrow_{book_id}"):
                msg = borrow_book(st.session_state.user_id, book_id)
                st.success(msg)
                st.rerun()

else:
    # Welcome Page for Unauthenticated Users
    st.markdown(
        """
        <div style="text-align:center; padding:50px; background-color:#f4f4f4; border-radius:10px;">
            <h1 style="color:#2E3B55; font-size:48px;">📚 Jaipur Central Library 📚</h1>
            <h3 style="color:#555;">"A gateway to knowledge and wisdom"</h3>
            <p style="color:#777; font-size:18px;">
                Welcome to Jaipur Central Library. Explore thousands of books, borrow and return with ease. 
                Please log in to continue.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
