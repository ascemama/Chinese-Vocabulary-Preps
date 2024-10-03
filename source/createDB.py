import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
connection = sqlite3.connect('./source/vocabulary.db')

# Create a cursor object
cursor = connection.cursor()

# Create a table named 'vocabulary' with columns for date, pinyin, and translation
# The pinyin column has a UNIQUE constraint
cursor.execute('''
CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY,
    date DATE,
    pinyin TEXT UNIQUE,
    translation TEXT
)
''')

# Commit the changes to the database
connection.commit()

# Close the cursor and connection
cursor.close()
connection.close()