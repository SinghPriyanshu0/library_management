from faker import Faker
import pandas as pd
import random

# Initialize Faker
fake = Faker()

# Number of Books (Adjust as needed)
num_books = 10000  

# Define possible genres
genres = ["Fiction", "Non-Fiction", "Mystery", "Science Fiction", "Fantasy", 
          "Biography", "History", "Romance", "Horror", "Self-Help"]

# Generate Books Data
books_data = []
for i in range(1, num_books + 1):
    title = fake.sentence(nb_words=3).replace(".", "")
    author = fake.name()
    genre = random.choice(genres)
    year = random.randint(1900, 2024)  # Random year between 1900 and now
    available = True  # Default to available

    books_data.append({
        "book_id": i,
        "title": title,
        "author": author,
        "genre": genre,
        "year": year,
        "available": available
    })

# Convert to DataFrame
books_df = pd.DataFrame(books_data)

# Save to CSV
books_df.to_csv("books_data.csv", index=False)

# Preview Data
print(books_df.head())
print("\n✅ Successfully generated 10,000 books!")
