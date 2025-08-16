"""
Progress Tracking with SQLite and Spaced Repetition
Simple implementation without external dependencies
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class ProgressTracker:
    """Track user progress and implement spaced repetition."""
    
    def __init__(self, db_path: str = "progress.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        """Create necessary database tables."""
        cursor = self.conn.cursor()
        
        # User attempts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                verb TEXT NOT NULL,
                tense TEXT NOT NULL,
                person INTEGER NOT NULL,
                user_answer TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                is_correct BOOLEAN NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Verb performance table for spaced repetition
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verb_performance (
                verb TEXT NOT NULL,
                tense TEXT NOT NULL,
                person INTEGER NOT NULL,
                correct_count INTEGER DEFAULT 0,
                incorrect_count INTEGER DEFAULT 0,
                last_seen DATETIME,
                next_review DATETIME,
                difficulty_score REAL DEFAULT 0.5,
                PRIMARY KEY (verb, tense, person)
            )
        ''')
        
        # Session summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                total_attempts INTEGER DEFAULT 0,
                correct_attempts INTEGER DEFAULT 0,
                verbs_practiced TEXT
            )
        ''')
        
        self.conn.commit()
    
    def record_attempt(self, verb: str, tense: str, person: int, 
                      user_answer: str, correct_answer: str, is_correct: bool):
        """Record a single attempt."""
        cursor = self.conn.cursor()
        
        # Insert attempt
        cursor.execute('''
            INSERT INTO attempts (verb, tense, person, user_answer, correct_answer, is_correct)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (verb, tense, person, user_answer, correct_answer, is_correct))
        
        # Update verb performance
        cursor.execute('''
            INSERT INTO verb_performance (verb, tense, person, correct_count, incorrect_count, last_seen, next_review)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            ON CONFLICT(verb, tense, person) DO UPDATE SET
                correct_count = correct_count + ?,
                incorrect_count = incorrect_count + ?,
                last_seen = CURRENT_TIMESTAMP,
                next_review = ?,
                difficulty_score = CASE 
                    WHEN ? THEN MAX(0.1, difficulty_score - 0.15)
                    ELSE MIN(1.0, difficulty_score + 0.2)
                END
        ''', (verb, tense, person, 
              1 if is_correct else 0, 
              0 if is_correct else 1,
              self.calculate_next_review(is_correct),
              1 if is_correct else 0,
              0 if is_correct else 1,
              self.calculate_next_review(is_correct),
              is_correct))
        
        self.conn.commit()
    
    def calculate_next_review(self, is_correct: bool, current_interval: int = 1) -> str:
        """Calculate next review date based on performance."""
        if is_correct:
            # Successful: double the interval (1, 2, 4, 8, 16 days...)
            next_interval = min(current_interval * 2, 30)
        else:
            # Failed: reset to 1 day
            next_interval = 1
        
        next_date = datetime.now() + timedelta(days=next_interval)
        return next_date.isoformat()
    
    def get_verbs_for_review(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get verbs that need review based on spaced repetition."""
        cursor = self.conn.cursor()
        
        # Get items due for review
        cursor.execute('''
            SELECT verb, tense, person, difficulty_score,
                   correct_count, incorrect_count
            FROM verb_performance
            WHERE next_review <= CURRENT_TIMESTAMP
            ORDER BY difficulty_score DESC, next_review ASC
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_weak_areas(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Identify verbs/tenses user struggles with."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT verb, tense, person,
                   correct_count, incorrect_count,
                   CAST(correct_count AS REAL) / (correct_count + incorrect_count) as accuracy,
                   difficulty_score
            FROM verb_performance
            WHERE correct_count + incorrect_count >= 3
            ORDER BY accuracy ASC, difficulty_score DESC
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        cursor = self.conn.cursor()
        
        # Overall stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_attempts,
                SUM(is_correct) as correct_attempts,
                COUNT(DISTINCT verb) as unique_verbs,
                COUNT(DISTINCT tense) as unique_tenses
            FROM attempts
        ''')
        overall = dict(cursor.fetchone())
        
        # Calculate accuracy
        if overall['total_attempts'] > 0:
            overall['accuracy'] = (overall['correct_attempts'] / overall['total_attempts']) * 100
        else:
            overall['accuracy'] = 0
        
        # Best performing verbs
        cursor.execute('''
            SELECT verb, 
                   CAST(SUM(is_correct) AS REAL) / COUNT(*) * 100 as accuracy,
                   COUNT(*) as attempts
            FROM attempts
            GROUP BY verb
            HAVING attempts >= 5
            ORDER BY accuracy DESC
            LIMIT 5
        ''')
        overall['best_verbs'] = [dict(row) for row in cursor.fetchall()]
        
        # Most practiced tenses
        cursor.execute('''
            SELECT tense, COUNT(*) as count
            FROM attempts
            GROUP BY tense
            ORDER BY count DESC
        ''')
        overall['tense_distribution'] = [dict(row) for row in cursor.fetchall()]
        
        return overall
    
    def get_recent_mistakes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent mistakes for review."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT verb, tense, person, user_answer, correct_answer, timestamp
            FROM attempts
            WHERE is_correct = 0
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def start_session(self) -> int:
        """Start a new practice session."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (start_time, total_attempts, correct_attempts)
            VALUES (CURRENT_TIMESTAMP, 0, 0)
        ''')
        self.conn.commit()
        return cursor.lastrowid
    
    def update_session(self, session_id: int, total: int, correct: int, verbs: List[str]):
        """Update session statistics."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE sessions
            SET end_time = CURRENT_TIMESTAMP,
                total_attempts = ?,
                correct_attempts = ?,
                verbs_practiced = ?
            WHERE id = ?
        ''', (total, correct, json.dumps(verbs), session_id))
        self.conn.commit()
    
    def get_learning_curve(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get accuracy over time for learning curve visualization."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT DATE(timestamp) as date,
                   COUNT(*) as attempts,
                   SUM(is_correct) as correct,
                   CAST(SUM(is_correct) AS REAL) / COUNT(*) * 100 as accuracy
            FROM attempts
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(timestamp)
            ORDER BY date ASC
        ''', (days,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        self.conn.close()