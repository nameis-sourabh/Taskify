from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
from datetime import datetime, timedelta
import smtplib as s

app = Flask("__name__")
app.secret_key = 'your_secret_key' 

def limit_filter(sequence, n):
    return sequence[:n]

env = app.jinja_env
env.filters['limit'] = limit_filter


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    try:
        if session['email']:
            return redirect(url_for('dashboard'))
    except:
        return render_template('login.html')

@app.route('/login_verify', methods=['POST'])
def login_verify():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('registration.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Register WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()

        if user:
            session['email'] = email
            print("Session",session['email'])
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))
    return redirect(url_for('login'))


def time_difference_filter(contribution_datetime_str):
    contribution_datetime = datetime.strptime(contribution_datetime_str, '%Y-%m-%d')
    current_datetime = datetime.now()
    time_difference = contribution_datetime - current_datetime 
    return time_difference.days + 1

app.jinja_env.filters['time_difference'] = time_difference_filter
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('projects.db')
    cursor = conn.cursor()
    email = str(session['email'])
    cursor.execute("SELECT * FROM projects WHERE owner_email = ?;", (email,))
    projects = cursor.fetchall()
    return render_template('dashboard.html',projects = projects)
    try:
        conn = sqlite3.connect('projects.db')
        cursor = conn.cursor()
        email = str(session['email'])
        cursor.execute("SELECT * FROM projects WHERE owner_email = ?;", (email,))
        projects = cursor.fetchall()
        return render_template('dashboard.html',projects = projects)
    except:
        return redirect(url_for('login'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registration_verify', methods=['POST'])
def reg_verify():
    if request.method == 'POST':
        name = request.form['username']
        contactNo = request.form['contactNo']
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('registration.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Register (name, contactNo, email, password) VALUES (?, ?, ?, ?)", (name, contactNo, email, password))
            conn.commit()
            conn.close()
            session['email'] = email
            return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Error: Email or Contact Number already exists."

@app.route('/projects')
def projects():
    return render_template('project.html')


@app.route('/add_project', methods=['POST'])
def add_project():
    email = session['email']
    if request.method == 'POST':
        owner_name = request.form['owner_name']
        project_name = request.form['project_name']
        description = request.form['description']
        contributor_email = request.form['contributors_email']
        contribution_datetime = request.form['deadline']
        try:
            conn = sqlite3.connect('projects.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO projects (project_name, owner_name, owner_email, contributor_email, contribution_datetime, description) VALUES (?, ?, ?, ?,? ,?)", (project_name, owner_name, email, contributor_email, contribution_datetime, description))
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Error: Email or Contact Number already exists."
    return "Project is not created"



@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for("login"))


def sendMail(data):
    myemail = "kawadkardeepesh80@gmail.com"
    mypassword = "unbd yrnj jery pitq"
    ob= s.SMTP("smtp.gmail.com", 587)
    ob.ehlo()
    ob.starttls()
    ob.login(myemail, mypassword)
    subject = data['sub']
    message = data['msg']
    receiver = data['assigned_to'] 
    print('Sending mail ....')
    ob.sendmail(myemail, receiver, message)
    print('Mail sent')
    ob.quit()

def defaultNotification(data):
    project_name = data['project_name']
    owner = data['owner']
    assigned_to = data['assigned_to']
    task_assigned = data['task_assigned']
    ontime = "pending"
    day5 = "pending"
    day1 = "pending"
    hr1 = "pending"
    deadline = data['deadline']
    conn = sqlite3.connect('notification.db')
    cursor = conn.cursor()
    insert_data = (project_name, owner, task_assigned, assigned_to, ontime, day5, day1, hr1, deadline)
    insert_query = '''
    INSERT INTO notification (project_name, owner, task, assigned_to, ontime, day5, day1, hr1, deadline)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)
    '''
    cursor.execute(insert_query, insert_data)
    conn.commit()
    conn.close()
    print(data['msg'])

def ontimeNotification(data):
    conn = sqlite3.connect('notification.db')
    cur = conn.cursor()
    project_name = data['project_name']
    assigned_to = data['assigned_to']
    task_assigned = data['task_assigned']
    owner = data['owner']
    deadline = data['deadline']
    cur.execute('SELECT * FROM notification WHERE project_name=? AND assigned_to=? AND task=? AND owner=?', (project_name,assigned_to,task_assigned, owner))
    row = cur.fetchone()
   
    if row:
        row_id = row[0]
        ontime = 'sent'
        day5 = 'pending'
        day1 = 'pending'
        hr1 = 'pending'
        cur.execute('''
            UPDATE notification 
            SET 
            project_name = ?, 
            owner = ?, 
            task = ?, 
            assigned_to = ?, 
            ontime = ?, 
            day5 = ?, 
            day1 = ?, 
            hr1 = ?,
            deadline = ?
            WHERE notification_id = ?
        ''', (project_name, owner, task_assigned, assigned_to, ontime, day5, day1, hr1, deadline, row_id))
        conn.commit()

    conn.close()

    sendMail(data=data)
    print(data)
    print("onTime executed successfully")

def day5Notification(data):
    conn = sqlite3.connect('notification.db')
    cur = conn.cursor()
    project_name = data['project_name']
    assigned_to = data['assigned_to']
    task_assigned = data['task_assigned']
    deadline = data['deadline']
    owner = data['owner']
    deadline=data['deadline']
    days = time_difference_filter(deadline)
    if (days <= 5):
        data['msg'] = data['msg'] + "\n 5 Days left only for task completion."
        cur.execute('SELECT * FROM notification WHERE project_name=? AND assigned_to=? AND task=? AND owner=?', (project_name,assigned_to,task_assigned, owner))
        row = cur.fetchone()
    
        if row:
            row_id = row[0]
            ontime = 'sent'
            day5 = 'sent'
            day1 = 'pending'
            hr1 = 'pending'
            cur.execute('''
                UPDATE notification 
                SET 
                project_name = ?, 
                owner = ?, 
                task = ?, 
                assigned_to = ?, 
                ontime = ?, 
                day5 = ?, 
                day1 = ?, 
                hr1 = ?,
                deadline = ?
                WHERE notification_id = ?
            ''', (project_name, owner, task_assigned, assigned_to, ontime, day5, day1, hr1,deadline, row_id))
            conn.commit()

        conn.close()
        if (days >1):
            sendMail(data=data)

        print("onTime executed successfully")

def day1Notification(data):
    deadline=data['deadline']
    days = time_difference_filter(deadline)
    
    if (days <= 1):
        print(days)
        conn = sqlite3.connect('notification.db')
        cur = conn.cursor()
        project_name = data['project_name']
        assigned_to = data['assigned_to']
        task_assigned = data['task_assigned']
        deadline = data['deadline']
        owner = data['owner']
        data['msg'] = data['msg'] + "\n Only 1 Day left only for task completion. Do it fast."
        cur.execute('SELECT * FROM notification WHERE project_name=? AND assigned_to=? AND task=? AND owner=?', (project_name,assigned_to,task_assigned, owner))
        row = cur.fetchone()
    
        if row:
            row_id = row[0]
            ontime = 'sent'
            day5 = 'sent'
            day1 = 'sent'
            hr1 = 'pending'
            cur.execute('''
                UPDATE notification 
                SET 
                project_name = ?, 
                owner = ?, 
                task = ?, 
                assigned_to = ?, 
                ontime = ?, 
                day5 = ?, 
                day1 = ?, 
                hr1 = ?,
                deadline = ?
                WHERE notification_id = ?
            ''', (project_name, owner, task_assigned, assigned_to, ontime, day5, day1, hr1,deadline, row_id))
            conn.commit()

        conn.close()
        if (days >= 0):
            sendMail(data=data)

        print("onTime executed successfully")

def endNotification(data):
    deadline=data['deadline']
    days = time_difference_filter(deadline)
    if (days < 0):
        conn = sqlite3.connect('notification.db')
        cur = conn.cursor()
        project_name = data['project_name']
        assigned_to = data['assigned_to']
        task_assigned = data['task_assigned']
        deadline = data['deadline']
        owner = data['owner']
        data['msg'] = data['msg'] + "\n Now the deadline is over."
        cur.execute('SELECT * FROM notification WHERE project_name=? AND assigned_to=? AND task=? AND owner=?', (project_name,assigned_to,task_assigned, owner))
        row = cur.fetchone()
    
        if row:
            row_id = row[0]
            ontime = 'sent'
            day5 = 'sent'
            day1 = 'sent'
            hr1 = 'sent'
            cur.execute('''
                UPDATE notification 
                SET 
                project_name = ?, 
                owner = ?, 
                task = ?, 
                assigned_to = ?, 
                ontime = ?, 
                day5 = ?, 
                day1 = ?, 
                hr1 = ?,
                deadline = ?
                WHERE notification_id = ?
            ''', (project_name, owner, task_assigned, assigned_to, ontime, day5, day1, hr1,deadline, row_id))
            conn.commit()

        conn.close()

        sendMail(data=data)

        print("onTime executed successfully")


def checkNotification(data):
    project_name = data['project_name']
    owner = data['owner']
    assigned_to = data['assigned_to']
    task_assigned = data['task_assigned']
    deadline = data['deadline']
    con = sqlite3.connect('notification.db')
    cur = con.cursor()
    try:
        cur.execute('SELECT * FROM notification WHERE project_name = ? AND owner = ? AND assigned_to = ? AND task = ?', (project_name,owner,  assigned_to, task_assigned))
        notification_data = cur.fetchall()
        ontime = notification_data[0][5]
        day5 = notification_data[0][6]
        day1 = notification_data[0][7]
        hr1 = notification_data[0][8]
        if (ontime == "pending"):
            print("ONTIME EXECUTED")
            ontimeNotification(data=data)
        elif (ontime == "sent") and (day5 == "pending"):
            print("DAY5 EXECUTED")
            day5Notification(data=data)
        elif (ontime == "sent") and (day5 == "sent") and (day1 == "pending"):
            print("DAY1 EXECUTED")
            day1Notification(data=data)
        elif (ontime == "sent") and (day5 == "sent") and (day1 == "sent") and (hr1 == "pending"):
            print("END EXECUTED")
            endNotification(data=data)
    except:
        defaultNotification(data=data)
        print("Except block executed.")  

@app.route('/<project>')
def project(project):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    try :
        email = session['email']
    except :
        return redirect(url_for('login'))
    
    cursor.execute("SELECT * FROM Highest_Priority WHERE project = ?", ( project,))
    hp_tasks = cursor.fetchall()
    
    for task in hp_tasks:
        email_list = task[6]
        email_list = email_list.split(",")
        subject = "Task assigned"
        message = f'''
        Hello sir / mam, You are invited to collaborate on a project and task assigned has highest priority.
        Sender's email:- {task[1]}
        Project :- {task[2]}
        Task name :- {task[3]}
        Task description :- {task[4]}
        Deadline :- {task[5]}
        Assigned to :- {task[6]}'''
        
        for email_assigned in email_list:
            data = {
            "msg" : message,
            "sub" : subject,
            'assigned_to' : email_assigned,
            'task_assigned' : task[3],
            'project_name' :task[2],
            'owner' : task[1],
            'deadline' : task[5]
            }
            checkNotification(data=data)


    cursor.execute("SELECT * FROM Medium_Priority WHERE project = ?", ( project,))
    mp_tasks = cursor.fetchall()

    for task in mp_tasks:
        email_list = task[6]
        email_list = email_list.split(",")
        subject = "Task assigned"
        message = f'''
        Hello sir / mam, You are invited to collaborate on a project and task assigned has medium priority.
        Sender's email:- {task[1]}
        Project :- {task[2]}
        Task name :- {task[3]}
        Task description :- {task[4]}
        Deadline :- {task[5]}
        Assigned to :- {task[6]}'''
        
        for email_assigned in email_list:
            data = {
            "msg" : message,
            "sub" : subject,
            'assigned_to' : email_assigned,
            'task_assigned' : task[3],
            'project_name' :task[2],
            'owner' : task[1],
            'deadline' : task[5]
            }
            checkNotification(data=data)

    cursor.execute("SELECT * FROM Low_Priority WHERE project = ?", (project,))
    lp_tasks = cursor.fetchall()

    for task in lp_tasks:
        email_list = task[6]
        email_list = email_list.split(",")
        subject = "Task assigned"
        message = f'''
        Hello sir / mam, You are invited to collaborate on a project and task assigned has low priority.
        Sender's email:- {task[1]}
        Project :- {task[2]}
        Task name :- {task[3]}
        Task description :- {task[4]}
        Deadline :- {task[5]}
        Assigned to :- {task[6]}'''
        
        for email_assigned in email_list:
            data = {
            "msg" : message,
            "sub" : subject,
            'assigned_to' : email_assigned,
            'task_assigned' : task[3],
            'project_name' :task[2],
            'owner' : task[1],
            'deadline' : task[5]
            }
            checkNotification(data=data)

    cursor.execute("SELECT * FROM Additional_Task WHERE project = ?", (project,))
    a_tasks = cursor.fetchall()
    
    for task in a_tasks:
        email_list = task[6]
        email_list = email_list.split(",")
        subject = "Task assigned"
        message = f'''
        Hello sir / mam, You are invited to collaborate on a project and this is additional task.
        Sender's email:- {task[1]}
        Project :- {task[2]}
        Task name :- {task[3]}
        Task description :- {task[4]}
        Deadline :- {task[5]}
        Assigned to :- {task[6]}'''
        
        for email_assigned in email_list:
            data = {
            "msg" : message,
            "sub" : subject,
            'assigned_to' : email_assigned,
            'task_assigned' : task[3],
            'project_name' :task[2],
            'owner' : task[1],
            'deadline' : task[5]
            }
            checkNotification(data=data)

    conn = sqlite3.connect('Chats.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Chats WHERE project_name = ? ", (project, ))
    chats = cursor.fetchall()
    chats = list(reversed(chats))

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Highest_Priority WHERE project = ?", (project, ))
    HP_TASKS = cursor.fetchall()
    cursor.execute("SELECT * FROM Medium_Priority WHERE project = ?", (project, ))
    MP_TASKS = cursor.fetchall()
    cursor.execute("SELECT * FROM Low_Priority WHERE project = ?", (project, ))
    LP_TASKS = cursor.fetchall()
    cursor.execute("SELECT * FROM Additional_Task WHERE project = ?", (project, ))
    A_TASKS = cursor.fetchall()

    COMPLETE_TASK = [HP_TASKS, MP_TASKS, LP_TASKS, A_TASKS]
    access_email = []
    for cat in COMPLETE_TASK:
        for task in HP_TASKS:
            access_email.append(task[1])
            contributor_email = str(task[6])
            contributor_email = contributor_email.split(",")
            for i in contributor_email:
                access_email.append(i)
    
    access_email.append(session['email'])
    access_email = set(access_email)
    print("Access" ,access_email)
    print('Email', email)
    if (email in access_email):
        return render_template('project.html',project=project,hp_tasks = hp_tasks,mp_tasks=mp_tasks,lp_tasks=lp_tasks,a_tasks=a_tasks,chats=chats)
    else:
        return "Not accessible"
@app.route('/add_task', methods=['POST'])
def add_task():
    if request.method == 'POST':
        table = request.form['priority']
        email = session['email']
        project = request.form['project_name']
        print(project)
        task_name = request.form['task_name']
        description = request.form['description']
        assigned_to = request.form['assigned_to']
        deadline = request.form['deadline']
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {table} (email,project, task_name , description, deadline, assigned_to) VALUES (?, ?, ?, ?, ?,?)", (email, project, task_name, description, deadline, assigned_to))
        conn.commit()
        conn.close()
        conn = sqlite3.connect('notification.db')
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO notification (project_name, owner, task, assigned_to, ontime , day5 , day1 , hr1, deadline) VALUES (?, ?, ?, ?, ?,?, ?, ?, ?)", (project, email,  task_name, assigned_to, "pending", "pending", "pending", "pending", deadline))
        conn.commit()
        conn.close()
        return redirect(project)
    return "Project is not created"


@app.route('/delete_task/<project>/<table>/<id>')
def delete_task(project,table,id):
    email = session['email']
    
    if (table == "hp"):
        table = "Highest_Priority"
    elif (table == "mp"):
        table = "Medium_Priority"
    elif (table == "lp"):
        table = "Low_Priority"
    elif (table == "at"):
        table = "Additional_Task"
    else:
        return "Unknown table name"
    try:
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE project = ? AND email = ? AND task_id = ?", (project, email,  id))
        conn.commit()
    except sqlite3.Error as e:
        print("SQLite error:", e)

    finally:
        conn.close()
    project = "/" + project
    return redirect(project)

@app.route('/delete_project/<project_id>')
def delete_project(project_id):
    email = session['email']
    project_id = project_id
    try:
        conn = sqlite3.connect('projects.db')
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM projects WHERE id = ? AND owner_email = ?", (project_id, email))
        conn.commit()
    except sqlite3.Error as e:
        print("SQLite error:", e)

    finally:
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/add_chat', methods=['POST'])
def add_chat():
    now = datetime.now()
    formatted_time= str(now)
    if request.method == 'POST':
        message = request.form['message']
        user_email = session['email']
        project_name = request.form['project_name']
        try:
            conn = sqlite3.connect('registration.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Register WHERE email = ?", (user_email,))
            user_data = cursor.fetchone()
            user_name = user_data[1]
            conn = sqlite3.connect('Chats.db')
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO Chats (project_name, user_name, datetime, message) VALUES (?, ?, ?, ?)", (project_name, user_name, formatted_time, message))
            conn.commit()
            conn.close()
            return redirect(project_name)
        except sqlite3.IntegrityError:
            conn.close()
            return "Error: Email or Contact Number already exists."
    return "Project is not created"

@app.route('/delete_chat/<project>/<unique_id>')
def delete_chat(project,unique_id):
    unique_id = unique_id
    project= project
    conn = sqlite3.connect('Chats.db')
    c = conn.cursor()
    c.execute("DELETE FROM Chats WHERE chat_id = ?", (unique_id,))
    project = "/" + project
    return redirect(project)

if __name__ == "__main__" :
    app.run(debug=True)	