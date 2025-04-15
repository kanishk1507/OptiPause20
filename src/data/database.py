import os
import sqlite3
import threading
from pathlib import Path

class Database:
    """SQLite database manager for the eye care application."""
    
    # Singleton instance
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Create data directory in user's home folder
        self.data_dir = Path.home() / ".eyecare_app"
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.db_path = self.data_dir / "eyecare.db"
        self.conn = None
        self._connect()
        self._create_tables()
        self._initialized = True
    
    def _connect(self):
        """Connect to the SQLite database."""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return results as dictionary-like objects
    
    def _create_tables(self):
        """Create necessary database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Sessions table - tracks each work session
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            duration_seconds INTEGER,
            breaks_taken INTEGER DEFAULT 0
        )
        ''')
        
        # Breaks table - tracks each break
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS breaks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            start_time TIMESTAMP NOT NULL,
            duration_seconds INTEGER,
            completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
        ''')
        
        # Daily stats table - aggregated daily statistics
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            date TEXT PRIMARY KEY,
            total_work_seconds INTEGER DEFAULT 0,
            total_breaks INTEGER DEFAULT 0,
            completed_breaks INTEGER DEFAULT 0,
            longest_session_seconds INTEGER DEFAULT 0
        )
        ''')
        
        # Settings table - user preferences
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        ''')
        
        # Insert default settings if they don't exist
        default_settings = [
            ('work_duration', '1200'),  # 20 minutes in seconds
            ('break_duration', '20'),   # 20 seconds
            ('inactivity_threshold', '300'),  # 5 minutes in seconds
            ('notification_style', 'center'),
            ('sound_enabled', 'false'),
            ('selected_sound', 'none')
        ]
        
        cursor.executemany('''
        INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
        ''', default_settings)
        
        self.conn.commit()
    
    def get_setting(self, key, default=None):
        """Get a setting value by key."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        return result['value'] if result else default
    
    def set_setting(self, key, value):
        """Set a setting value."""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        ''', (key, str(value)))
        self.conn.commit()
    
    def start_session(self, start_time):
        """Record the start of a new work session."""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO sessions (start_time) VALUES (?)
        ''', (start_time,))
        self.conn.commit()
        return cursor.lastrowid
    
    def end_session(self, session_id, end_time, duration, breaks_taken):
        """Record the end of a work session."""
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE sessions 
        SET end_time = ?, duration_seconds = ?, breaks_taken = ?
        WHERE id = ?
        ''', (end_time, duration, breaks_taken, session_id))
        self.conn.commit()
    
    def record_break(self, session_id, start_time):
        """Record the start of a break."""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO breaks (session_id, start_time) VALUES (?, ?)
        ''', (session_id, start_time))
        self.conn.commit()
        return cursor.lastrowid
    
    def complete_break(self, break_id, duration):
        """Mark a break as completed."""
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE breaks 
        SET duration_seconds = ?, completed = 1
        WHERE id = ?
        ''', (duration, break_id))
        self.conn.commit()
    
    def update_daily_stats(self, date, work_seconds, breaks, completed_breaks, session_seconds):
        """Update the daily statistics."""
        cursor = self.conn.cursor()
        
        # First check if the date already exists
        cursor.execute('SELECT * FROM daily_stats WHERE date = ?', (date,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record
            cursor.execute('''
            UPDATE daily_stats 
            SET total_work_seconds = total_work_seconds + ?,
                total_breaks = total_breaks + ?,
                completed_breaks = completed_breaks + ?,
                longest_session_seconds = MAX(longest_session_seconds, ?)
            WHERE date = ?
            ''', (work_seconds, breaks, completed_breaks, session_seconds, date))
        else:
            # Create new record
            cursor.execute('''
            INSERT INTO daily_stats 
            (date, total_work_seconds, total_breaks, completed_breaks, longest_session_seconds)
            VALUES (?, ?, ?, ?, ?)
            ''', (date, work_seconds, breaks, completed_breaks, session_seconds))
            
        self.conn.commit()
    
    def get_streak_data(self, days=30):
        """Get data for calculating user's streak."""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT date, total_breaks, completed_breaks 
        FROM daily_stats 
        ORDER BY date DESC 
        LIMIT ?
        ''', (days,))
        return cursor.fetchall()
    
    def get_screen_time_stats(self, days=7):
        """Get screen time statistics for the specified number of past days."""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT date, total_work_seconds, total_breaks, completed_breaks 
        FROM daily_stats 
        ORDER BY date DESC 
        LIMIT ?
        ''', (days,))
        return cursor.fetchall()
        
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
