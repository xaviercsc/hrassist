#!/usr/bin/env python3
"""
Script to update the database schema with new columns for the Job model
"""

import sqlite3
import os
from pathlib import Path

def update_database_schema():
    """Add missing columns to the jobs table"""
    
    # Find the database file
    db_path = "hr_assist.db"
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(jobs)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Add missing columns one by one
        columns_to_add = [
            ("salary_range", "VARCHAR(100)"),
            ("employment_type", "VARCHAR(50) NOT NULL DEFAULT 'full-time'"),
            ("closed_date", "DATETIME"),
            ("close_reason", "VARCHAR(200)")
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE jobs ADD COLUMN {column_name} {column_type}"
                    print(f"Adding column: {sql}")
                    cursor.execute(sql)
                    print(f"✅ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"❌ Error adding column {column_name}: {e}")
            else:
                print(f"⏩ Column {column_name} already exists")
        
        # Check if Interview table exists, if not create it
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interviews'")
        if not cursor.fetchone():
            print("Creating interviews table...")
            create_interviews_table = """
            CREATE TABLE interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                interview_type VARCHAR(50) NOT NULL,
                interview_date DATETIME NOT NULL,
                interview_time VARCHAR(10) NOT NULL,
                duration_minutes INTEGER NOT NULL,
                timezone VARCHAR(50),
                platform VARCHAR(50),
                meeting_link VARCHAR(500),
                meeting_password VARCHAR(100),
                notes TEXT,
                result VARCHAR(20),
                feedback TEXT,
                conducted_date DATETIME,
                created_by INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES applications (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
            """
            cursor.execute(create_interviews_table)
            print("✅ Created interviews table")
        else:
            print("⏩ Interviews table already exists")
        
        # Check if applications table has the new columns
        cursor.execute("PRAGMA table_info(applications)")
        app_columns = [row[1] for row in cursor.fetchall()]
        
        app_columns_to_add = [
            ("technical_interview_date", "DATETIME"),
            ("hr_interview_date", "DATETIME"),
            ("willingness_deadline", "DATETIME"),
            ("willingness_confirmed", "BOOLEAN"),
            ("willingness_response_date", "DATETIME"),
            ("selected_date", "DATETIME"),
            ("hired_date", "DATETIME"),
            ("rejection_reason", "TEXT")
        ]
        
        for column_name, column_type in app_columns_to_add:
            if column_name not in app_columns:
                try:
                    sql = f"ALTER TABLE applications ADD COLUMN {column_name} {column_type}"
                    print(f"Adding application column: {sql}")
                    cursor.execute(sql)
                    print(f"✅ Added application column: {column_name}")
                except sqlite3.Error as e:
                    print(f"❌ Error adding application column {column_name}: {e}")
            else:
                print(f"⏩ Application column {column_name} already exists")
        
        # Commit changes
        conn.commit()
        print("\n✅ Database schema updated successfully!")
        
        # Show updated table structure
        cursor.execute("PRAGMA table_info(jobs)")
        print("\nUpdated jobs table structure:")
        for row in cursor.fetchall():
            print(f"  {row[1]} - {row[2]}")
            
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔄 Updating database schema...")
    success = update_database_schema()
    if success:
        print("\n🎉 Database update completed successfully!")
        print("You can now restart your application.")
    else:
        print("\n💥 Database update failed!")
