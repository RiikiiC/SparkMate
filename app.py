from flask import Flask, render_template, request, session, redirect, jsonify
from dotenv import load_dotenv
import os
import mysql.connector

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

def get_db():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        port=8889
    )

def get_user():
    return session.get("user")

@app.route("/")
def homepage():

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM activities
        ORDER BY created_at DESC
        LIMIT 4
    """)
    recent_event = cursor.fetchall()

    for activity in recent_event:
        cursor.execute(
            "SELECT COUNT(*) AS likes_count FROM Likes WHERE activity_id = %s", 
            (activity["id"], )
        )
        count = cursor.fetchone()
        if count:
            activity["likes_count"] = count["likes_count"]

    cursor.execute("""
        SELECT * FROM activities
        WHERE circle = 'Museum'
        ORDER BY created_at DESC
        LIMIT 5
    """)
    museum_circle = cursor.fetchall()

    cursor.execute("""
        SELECT * FROM activities
        WHERE circle = 'Market'
        ORDER BY created_at DESC
        LIMIT 5
    """)
    market_circle = cursor.fetchall()

    cursor.execute("""
        SELECT * FROM activities
        WHERE circle = 'Sports'
        ORDER BY created_at DESC
        LIMIT 5
    """)
    sports_circle = cursor.fetchall()

    return render_template("home.html",
                            user=get_user(),
                            recent_event=recent_event,
                            museum_circle=museum_circle,
                            market_circle=market_circle,
                            sports_circle=sports_circle)




@app.route("/events")
def events_list():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""SELECT * FROM activities""")
    events = cursor.fetchall()

    for activity in events:
        cursor.execute(
            "SELECT COUNT(*) AS likes_count FROM Likes WHERE activity_id = %s", 
            (activity["id"], )
        )
        count = cursor.fetchone()
        if count:
            activity["likes_count"] = count["likes_count"]

    return render_template("events.html",
                            user=get_user(),
                            events=events)

@app.route("/circle/<circle_name>")
def circle_list(circle_name):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM activities
        WHERE circle = %s
        ORDER BY created_at DESC
    """, (circle_name,))
    events = cursor.fetchall()

    return render_template("circle.html",
                           user=get_user(),
                           circle_name=circle_name,
                           events=events)

@app.route("/circles")
def circle():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM activities
        WHERE circle = 'Museum'
        ORDER BY created_at DESC
        LIMIT 5
    """)
    museum_circle = cursor.fetchall()

    cursor.execute("""
        SELECT * FROM activities
        WHERE circle = 'Market'
        ORDER BY created_at DESC
        LIMIT 5
    """)
    market_circle = cursor.fetchall()

    cursor.execute("""
        SELECT * FROM activities
        WHERE circle = 'Sports'
        ORDER BY created_at DESC
        LIMIT 5
    """)
    sports_circle = cursor.fetchall()

    return render_template("circles.html",
                            user=get_user(),
                            museum_circle=museum_circle,
                            market_circle=market_circle,
                            sports_circle=sports_circle)


# register page

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/process-register", methods=['POST'])
def process_register():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute('''INSERT INTO `users` (username, email, password)
        VALUES (%s, %s, %s)
            ''', (username, email, password))
    conn.commit()

    return render_template("login.html")


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/process-login", methods=['POST'])
def process_login():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)


    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute('''SELECT * 
                    FROM `users` 
                    WHERE `email` = %s 
                    AND `password` = %s''',(email, password))
    
    user = cursor.fetchone()

    if user:
        session['user'] = user
        return redirect("/")
    else:
        return render_template("not-logged-in.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



# activity

@app.route("/activity/<int:activity_id>")
def activity(activity_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''SELECT a.*, u.name AS organizer_name
        FROM activities AS a
        LEFT JOIN users AS u
            ON a.organizer_id = u.id
        WHERE a.id = %s''', (activity_id,))
    activity = cursor.fetchone()
    
    user_liked = False
    user = get_user()
    if user:
        cursor.execute(
            "SELECT id FROM Likes WHERE user_id = %s AND activity_id = %s", 
            (user['id'], activity_id)
        )
        result = cursor.fetchone()
        if result:
            user_liked = True


    cursor.execute(
        "SELECT COUNT(*) AS likes_count FROM Likes WHERE activity_id = %s", 
        (activity_id, )
    )
    count = cursor.fetchone()
    if count:
        activity["likes_count"] = count["likes_count"]

    return render_template("activity.html", 
                           activity=activity, userliked=user_liked, user=user)


@app.route("/like/<int:activity_id>", methods=['POST'])
def like(activity_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    user = get_user()
    if not user:
        return jsonify({"success": False, "error": "not_logged_in"})
    
    user_id = user["id"]

    cursor.execute(
        "SELECT id FROM Likes WHERE user_id = %s AND activity_id = %s LIMIT 1", 
        (user_id, activity_id)
    )
    liked = cursor.fetchone()

    if liked:
        cursor.execute(
            "DELETE FROM Likes WHERE id = %s", 
            (liked['id'],)
        )
        conn.commit()
        user_liked = False
    else:
        cursor.execute(
            "INSERT INTO Likes (user_id, activity_id) VALUES (%s, %s)", 
            (user_id, activity_id)
        )
        conn.commit()
        user_liked = True

    cursor.execute(
        "SELECT COUNT(*) AS likes_count FROM Likes WHERE activity_id = %s", 
        (activity_id, )
    )
    count = cursor.fetchone()
    if count:
        likes_count = count["likes_count"]

    return jsonify({
        "success": True,"userliked":user_liked,"likes_count":likes_count
    })


# create page

@app.route("/create", methods=["GET", "POST"])
def create():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    user = get_user()
    if not user:
        return redirect("/login")
    


    if request.method == "GET":
        return render_template("create-activity.html", user=user)
    organizer_id = user["id"]

    title = request.form.get("title")
    detail = request.form.get("detail")
    circle = request.form.get("circle")
    event_date = request.form.get("event_date")
    time_start = request.form.get("time_start")
    time_end = request.form.get("time_end")
    location = request.form.get("location")
    budget = request.form.get("budget")

    picture = request.files.get("picture")
    
    cover_image = None
    if picture and picture.filename != "":
        cover_image = picture.filename
        picture.save(f"static/images/activity_pic/{picture.filename}")

    cursor.execute("""
        INSERT INTO activities
        (title, detail, circle, time_start, time_end, event_date, location, budget, cover_image, organizer_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (title, detail, circle, time_start, time_end, event_date, location, budget, cover_image, organizer_id))

    conn.commit()

    return redirect("/")


# account page
@app.route("/account")
def account():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    user = get_user()
    if not user:
        return redirect("/login")

    cursor.execute("""
        SELECT *
        FROM activities
        WHERE organizer_id = %s
        ORDER BY created_at DESC
    """, (user["id"],))
    activities = cursor.fetchall()

    posts_count = len(activities)

    return render_template("account.html", activities=activities, user=user, posts_count=posts_count)

@app.route("/activity-edit/<int:activity_id>", methods=['GET', 'POST'])
def activity_edit(activity_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    user = get_user()
    if not user:
        return redirect("/login")
    
    if request.method == 'GET':
        cursor.execute("SELECT * FROM activities WHERE id = %s", (activity_id,))
        activity = cursor.fetchone()
        return render_template("activity-edit.html", activity=activity, user=user)
    
    if request.method == 'POST':
        title = request.form.get('title')
        detail = request.form.get('detail')
        event_date = request.form.get('event_date')
        time_start = request.form.get('time_start')
        time_end = request.form.get('time_end')
        location = request.form.get('location')
        budget = request.form.get('budget')

        cursor.execute(
            "UPDATE activities SET title = %s, detail = %s,  event_date = %s,  time_start = %s,  time_end = %s,  location = %s,  budget = %s WHERE id = %s",
            (title, detail, event_date, time_start, time_end, location, budget, activity_id)
        )            
        conn.commit()

        return redirect(f"/activity/{activity_id}")


@app.route("/activity-delete/<int:activity_id>", methods=['GET', 'POST'])
def activity_delete(activity_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    user = get_user()
    if not user:
        return redirect("/login")
    
    if request.method == 'GET':
        cursor.execute("SELECT * FROM activities WHERE id = %s", (activity_id,))
        activity = cursor.fetchone()
        return render_template("activity-delete.html", activity=activity, user=user)
    
    if request.method == 'POST':
        cursor.execute(
            "DELETE FROM activities WHERE id = %s", 
            (activity_id,)
        )            
        conn.commit()

        return redirect("/account")


# contact organizer
@app.route("/organizer/<int:user_id>")
def organizer_profile(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    user = get_user()
    if not user:
        return redirect("/login")

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    organizer = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM activities
        WHERE organizer_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    activities = cursor.fetchall()

    posts_count = len(activities)

    return render_template(
        "organizer.html",
        user=user,
        organizer=organizer,
        activities=activities,
        posts_count=posts_count
    )


