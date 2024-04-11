import sqlite3

# Function to create the table if it doesn't exist

registration = '''CREATE TABLE IF NOT EXISTS Register (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        contactNo INTEGER UNIQUE,
                        email TEXT UNIQUE,
                        password TEXT)'''



projects = '''CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    project_name TEXT,
    owner_name TEXT,
    owner_email TEXT,
    contributor_email TEXT,
    contribution_datetime TEXT ,
    description TEXT
)
'''

highest_priority_Tasks = '''CREATE TABLE IF NOT EXISTS Highest_Priority (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    project TEXT NOT NULL,
    task_name TEXT NOT NULL,
    description TEXT,
    deadline DATE,
    assigned_to TEXT
);
'''

Medium_priority_Tasks = '''CREATE TABLE IF NOT EXISTS Medium_Priority (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    project TEXT NOT NULL,
    task_name TEXT NOT NULL,
    description TEXT,
    deadline DATE,
    assigned_to TEXT
);
'''
Low_priority_Tasks = '''CREATE TABLE IF NOT EXISTS Low_Priority (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    project TEXT NOT NULL,
    task_name TEXT NOT NULL,
    description TEXT,
    deadline DATE,
    assigned_to TEXT
);
'''
Additional_Tasks = '''CREATE TABLE IF NOT EXISTS Additional_Task (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    project TEXT NOT NULL,
    task_name TEXT NOT NULL,
    description TEXT,
    deadline DATE,
    assigned_to TEXT
);
'''

Chat = '''CREATE TABLE IF NOT EXISTS Chats (
  chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_name TEXT NOT NULL,
  user_name TEXT NOT NULL,
  datetime TEXT NOT NULL,
  message TEXT NOT NULL
);
'''

notificaiton = '''CREATE TABLE IF NOT EXISTS notification (
  notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_name TEXT NOT NULL,
  owner TEXT NOT NULL,
  task TEXT NOT NULL,
  assigned_to TEXT NOT NULL,
  ontime TEXT NOT NULL,
  day5 TEXT NOT NULL,
  day1 TEXT NOT NULL,
  hr1 TEXT NOT NULL,
  deadline TEXT NOT NULL
);
'''

def create_table(cmd = '', file = ''):
    conn =sqlite3.connect(file)
    cursor = conn.cursor()
    cursor.execute(cmd)
    conn.commit()
    conn.close()

create_table(cmd = registration, file = 'registration.db')
create_table(cmd=projects, file='projects.db')
create_table(cmd=highest_priority_Tasks, file='tasks.db')
create_table(cmd=Medium_priority_Tasks, file='tasks.db')
create_table(cmd=Low_priority_Tasks, file='tasks.db')
create_table(cmd=Additional_Tasks, file='tasks.db')
create_table(cmd=Chat, file='Chats.db')
create_table(cmd=notificaiton, file='notification.db')