import os
import sqlite3
import json

# BASE_DIR will be provided by main.py
DATABASE_TYPE = "sqlite3"
DATABASE_NAME = "database.db"

def initialize(base_dir):
    """Initialize database configuration with the provided base directory."""
    global BASE_DIR, DATABASE_DIR, DATABASE_PATH, TABLES_CONFIG_FILE
    
    BASE_DIR = base_dir
    DATABASE_DIR = os.path.join(BASE_DIR, "database")
    DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)
    TABLES_CONFIG_FILE = os.path.join(DATABASE_DIR, "db_tables_to_create.json")
    
    return DATABASE_PATH

def check_and_create_database():
    """Check if the database directory exists, create it if not, and create the database file."""
    # Check if the database directory exists, create it if not
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
    
    # Check if the database file exists, create it if not
    if not os.path.exists(DATABASE_PATH):
        conn = sqlite3.connect(DATABASE_PATH)
        conn.close()
        print(f"Database file created at: {DATABASE_PATH}")
        return True  # Indicates a new database was created
    return False  # Indicates the database already existed

def load_tables_config():
    """Load the tables configuration from the JSON file."""
    if os.path.exists(TABLES_CONFIG_FILE):
        with open(TABLES_CONFIG_FILE, 'r') as file:
            tables_config = json.load(file)
        return tables_config
    else:
        print(f"Configuration file not found: {TABLES_CONFIG_FILE}")
        return None
    
def create_tables(conn, tables_config):
    """Create tables in the database based on the configuration."""
    cursor = conn.cursor()
    
    for table_name, table_info in tables_config.items():
        # Process column definitions from the "field" array
        columns = []
        for field in table_info.get('field', []):
            column_def = f"{field[0]} {field[1]}"
            # Add any constraints if present
            if len(field) > 2:
                column_def += f" {field[2]}"
            columns.append(column_def)
        
        # Join all column definitions
        columns_sql = ", ".join(columns)
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
        cursor.execute(create_table_query)
        
        # Insert initial data if available
        initial_data = table_info.get('initial_data', [])
        if initial_data:
            # Get the column names from field definitions
            column_names = [field[0] for field in table_info.get('field', [])]
            placeholders = ", ".join(["?" for _ in range(len(column_names))])
            
            insert_query = f"INSERT OR IGNORE INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
            for row in initial_data:
                cursor.execute(insert_query, row)
    
    conn.commit()
    
def main(base_dir=None):
    """Main function to check and create the database and tables."""
    if base_dir:
        initialize(base_dir)
    else:
        # Fallback to the old behavior if no base_dir is provided
        global BASE_DIR
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.dirname(BASE_DIR)  # Go up one level to avoid database/database
        initialize(BASE_DIR)
        
    # Check if database file exists and create it if not
    is_new_db = check_and_create_database()
    
    # Always load tables and insert data
    # This ensures tables are created even if database file already exists
    # Load the tables configuration
    tables_config = load_tables_config()
    
    if tables_config:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        
        # Create tables based on the configuration
        create_tables(conn, tables_config)
        
        # Close the connection
        conn.close()
    else:
        print("No tables created due to missing configuration.")
    
    return DATABASE_PATH

def get_database_path():
    """Return the path to the database file."""
    return DATABASE_PATH
def get_database_type():
    """Return the type of the database."""
    return DATABASE_TYPE
def get_database_dir():
    """Return the directory where the database is located.""" 
    return DATABASE_DIR
def get_tables_config_file():
    """Return the path to the tables configuration file."""
    return TABLES_CONFIG_FILE
def get_tables_config():
    """Return the loaded tables configuration."""
    return load_tables_config()
def connect_to_database():
    """Connect to the database and return the connection object."""
    conn = sqlite3.connect(DATABASE_PATH)
    return conn
def close_database_connection(conn):
    """Close the database connection."""
    conn.close()