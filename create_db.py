import sqlite3
from hashlib import sha256

import sqlite3
from hashlib import sha256

def create_database():
    # Connect to SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect('summary_evaluation.db')

    # Create a cursor object
    cursor = conn.cursor()

    # Create table 'annotators'
    cursor.execute('''
        CREATE TABLE annotators (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')

    # Create table 'transcripts'
    cursor.execute('''
        CREATE TABLE transcripts (
            id INTEGER PRIMARY KEY,
            file_path TEXT NOT NULL UNIQUE
        )
    ''')

    # Create table 'summaries'
    cursor.execute('''
        CREATE TABLE summaries (
            id INTEGER PRIMARY KEY,
            transcript_id INTEGER,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL UNIQUE,
            FOREIGN KEY(transcript_id) REFERENCES transcripts(id)
        )
    ''')

    # Create table 'summary_evaluation'
    cursor.execute('''
        CREATE TABLE summary_evaluation (
            id INTEGER PRIMARY KEY,
            annotator_id INTEGER,
            summary_id INTEGER,
            adequacy_rating INTEGER,
            fluency_rating INTEGER,
            grammatical_correctness_rating INTEGER,
            FOREIGN KEY(annotator_id) REFERENCES annotators(id),
            FOREIGN KEY(summary_id) REFERENCES summaries(id)
        )
    ''')

    # Create table 'fact_check'
    cursor.execute('''
        CREATE TABLE fact_check (
            id INTEGER PRIMARY KEY,
            summary_evaluation_id INTEGER,
            span_start INTEGER,
            span_end INTEGER,
            is_factually_correct BOOLEAN,
            FOREIGN KEY(summary_evaluation_id) REFERENCES summary_evaluation(id)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def add_transcript(file_path):
    # Connect to SQLite database
    conn = sqlite3.connect('summary_evaluation.db')

    # Create a cursor object
    cursor = conn.cursor()

    # Insert a new transcript
    cursor.execute('''
        INSERT INTO transcripts (file_path)
        VALUES (?)
    ''', (file_path,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def create_annotator(username, password):
    # Connect to SQLite database
    conn = sqlite3.connect('summary_evaluation.db')

    # Create a cursor object
    cursor = conn.cursor()

    # Encrypt the password
    password_hash = sha256(password.encode('utf-8')).hexdigest()

    # Insert a new annotator
    cursor.execute('''
        INSERT INTO annotators (username, password_hash)
        VALUES (?, ?)
    ''', (username, password_hash))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def add_span(span_start, span_end, correct, annotator, summary_id):
    # Connect to SQLite database
    conn = sqlite3.connect('summary_evaluation.db')

    # Create a cursor object
    cursor = conn.cursor()

    # Get annotator's id
    cursor.execute('''
        SELECT id FROM annotators WHERE username = ?
    ''', (annotator,))
    annotator_id = cursor.fetchone()

    if annotator_id is None:
        print("Annotator does not exist.")
        return

    # Get the evaluation id
    cursor.execute('''
        SELECT id FROM summary_evaluation WHERE annotator_id = ? AND id = ?
    ''', (annotator_id[0], summary_id))
    evaluation_id = cursor.fetchone()

    if evaluation_id is None:
        print("Evaluation does not exist.")
        return

    # Insert a new fact check record
    cursor.execute('''
        INSERT INTO fact_check (summary_evaluation_id, span_start, span_end, is_factually_correct)
        VALUES (?, ?, ?, ?)
    ''', (evaluation_id[0], span_start, span_end, correct))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def add_summary(name, content, transcript_id):
    # Connect to SQLite database
    conn = sqlite3.connect('summary_evaluation.db')

    # Create a cursor object
    cursor = conn.cursor()

    # Get the transcript id
    cursor.execute('''
        SELECT id FROM transcripts WHERE id = ?
    ''', (transcript_id,))
    transcript_id_exists = cursor.fetchone()

    if transcript_id_exists is None:
        print("Transcript does not exist.")
        return

    # Insert a new summary
    cursor.execute('''
        INSERT INTO summaries (name, content, transcript_id)
        VALUES (?, ?, ?)
    ''', (name, content, transcript_id))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Call the function to create the database and tables
create_database()
add_transcript("Hi, how are you")
