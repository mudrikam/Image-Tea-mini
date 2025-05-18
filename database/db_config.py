import os
import sqlite3
import json
from core.utils.logger import log, debug, warning, error, exception

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
    
    debug(f"Database initialized: {DATABASE_PATH}")
    return DATABASE_PATH

def check_and_create_database():
    """Check if the database directory exists, create it if not, and create the database file."""
    # Check if the database directory exists, create it if not
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
        debug(f"Created database directory: {DATABASE_DIR}")
    
    # Check if the database file exists, create it if not
    if not os.path.exists(DATABASE_PATH):
        conn = sqlite3.connect(DATABASE_PATH)
        conn.close()
        log(f"Database file created at: {DATABASE_PATH}")
        return True  # Indicates a new database was created
    return False  # Indicates the database already existed

def load_tables_config():
    """Load the tables configuration from the JSON file."""
    if os.path.exists(TABLES_CONFIG_FILE):
        try:
            with open(TABLES_CONFIG_FILE, 'r') as file:
                tables_config = json.load(file)
            debug(f"Loaded tables configuration from: {TABLES_CONFIG_FILE}")
            return tables_config
        except json.JSONDecodeError as e:
            error(f"Invalid JSON in tables configuration: {e}")
            return None
        except Exception as e:
            exception(e, f"Error loading tables configuration")
            return None
    else:
        warning(f"Configuration file not found: {TABLES_CONFIG_FILE}")
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
        debug(f"Created or confirmed table: {table_name}")
        
        # Insert initial data if available
        initial_data = table_info.get('initial_data', [])
        if initial_data:
            # Get the column names from field definitions
            column_names = [field[0] for field in table_info.get('field', [])]
            placeholders = ", ".join(["?" for _ in range(len(column_names))])
            
            insert_query = f"INSERT OR IGNORE INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
            for row in initial_data:
                cursor.execute(insert_query, row)
            debug(f"Inserted {len(initial_data)} rows of initial data into {table_name}")
    
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
        warning("No base directory provided, using fallback location")
        
    # Check if database file exists and create it if not
    is_new_db = check_and_create_database()
    
    # Always load tables and insert data
    # This ensures tables are created even if database file already exists
    # Load the tables configuration
    tables_config = load_tables_config()
    
    if tables_config:
        # Connect to the database
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            
            # Create tables based on the configuration
            create_tables(conn, tables_config)
            
            # Close the connection
            conn.close()
            log(f"Database setup complete: {DATABASE_PATH}")
        except sqlite3.Error as e:
            error(f"SQLite error: {e}")
        except Exception as e:
            exception(e, "Unexpected error during database setup")
    else:
        error("No tables created due to missing configuration.")
    
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
    """Connect to the database and return the connection object with WAL mode enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    
    try:
        # Enable Write-Ahead Logging for better performance and concurrency
        conn.execute('PRAGMA journal_mode = WAL')  # Use WAL instead of rollback journal
        conn.execute('PRAGMA synchronous = NORMAL')  # Balance between safety and speed
        conn.execute('PRAGMA cache_size = 10000')  # 10MB cache (1 page = ~1KB)
        conn.execute('PRAGMA foreign_keys = ON')  # Enforce foreign key constraints
        conn.execute('PRAGMA temp_store = MEMORY')  # Store temp tables in memory
        
        # debug("Database connection established with WAL mode")
    except sqlite3.Error as e:
        error(f"Failed to enable WAL mode: {e}")
    
    return conn

def close_database_connection(conn):
    """Close the database connection."""
    if conn:
        conn.close()
        # debug("Database connection closed")

def optimize_database():
    """Run VACUUM and other optimizations on the database."""
    try:
        conn = connect_to_database()
        
        # Execute VACUUM to rebuild the database file, reclaiming unused space
        conn.execute('VACUUM')
        
        # Analyze the database to optimize query planning
        conn.execute('ANALYZE')
        
        # Checkpoint the WAL file to ensure changes are in the main database file
        conn.execute('PRAGMA wal_checkpoint(FULL)')
        
        close_database_connection(conn)
        log("Database optimized")
        return True
    except sqlite3.Error as e:
        error(f"Database optimization failed: {e}")
        return False

def get_database_stats():
    """Return statistics about the database."""
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        
        # Get page count and page size to calculate database size
        cursor.execute('PRAGMA page_count')
        page_count = cursor.fetchone()[0]
        
        cursor.execute('PRAGMA page_size')
        page_size = cursor.fetchone()[0]
        
        # Calculate size in MB
        db_size_mb = (page_count * page_size) / (1024 * 1024)
        
        # Get WAL file size if it exists
        wal_path = f"{DATABASE_PATH}-wal"
        wal_size_mb = 0
        if os.path.exists(wal_path):
            wal_size_mb = os.path.getsize(wal_path) / (1024 * 1024)
        
        # Get table list and row counts
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_stats = {}
        
        for table in tables:
            table_name = table[0]
            if not table_name.startswith('sqlite_'):
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                table_stats[table_name] = row_count
        
        close_database_connection(conn)
        
        return {
            "db_size_mb": db_size_mb,
            "wal_size_mb": wal_size_mb,
            "tables": table_stats
        }
    except sqlite3.Error as e:
        error(f"Failed to get database statistics: {e}")
        return None