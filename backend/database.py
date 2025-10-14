import sqlite3

# Connect to the SQLite database (this will create the file if it doesn't exist)
conn = sqlite3.connect('voters.db')
cursor = conn.cursor()

# SQL statement to create the 'voters' table
# status can be 'pending', 'approved', or 'rejected'
create_table_query = """
CREATE TABLE IF NOT EXISTS voters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    dob TEXT NOT NULL,
    aadhaar_hash TEXT NOT NULL UNIQUE,
    voter_id TEXT NOT NULL UNIQUE,
    phone_number TEXT NOT NULL,
    photo_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Execute the query and commit the changes
try:
    cursor.execute(create_table_query)
    conn.commit()
    print("Database and 'voters' table created successfully.")
except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    # Close the connection
    conn.close()
