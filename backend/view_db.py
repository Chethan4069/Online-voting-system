import sqlite3
import os

# --- Configuration ---
# Get the absolute path of the directory where this script is located
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Define database path relative to the script's location
DATABASE_NAME = os.path.join(BASE_DIR, 'voters.db')
TABLE_NAME = 'voters'

def view_voters():
    """Connects to the database and prints all records from the voters table."""
    
    if not os.path.exists(DATABASE_NAME):
        print(f"Error: The database file '{DATABASE_NAME}' was not found.")
        print("Please run 'python database.py' first to create it.")
        return

    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        print(f"--- Displaying all records from the '{TABLE_NAME}' table ---")
        
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        
        if not rows:
            print("The table is currently empty. No users have been registered yet.")
            return
            
        # Get column names from the cursor description
        column_names = [description[0] for description in cursor.description]
        
        # Print header
        print("\n" + " | ".join(f"{name:<20}" for name in column_names))
        print("-" * (23 * len(column_names))) # Separator line
        
        # Print each row
        for row in rows:
            # Format each value to be left-aligned within 20 characters
            # Truncate long values like the photo path or hash
            formatted_row = []
            for item in row:
                s_item = str(item)
                if len(s_item) > 18:
                    s_item = s_item[:15] + "..."
                formatted_row.append(f"{s_item:<20}")
            
            print(" | ".join(formatted_row))

    except sqlite3.Error as e:
        print(f"A database error occurred: {e}")
    finally:
        if conn:
            conn.close()

# --- Main Execution ---
if __name__ == '__main__':
    view_voters()
