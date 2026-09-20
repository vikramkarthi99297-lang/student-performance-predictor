from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

import pandas as pd
import mysql.connector

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score


# ==================================================
# FLASK APPLICATION
# ==================================================

app = Flask(__name__)

app.secret_key = "student-performance-secret-key"


# ==================================================
# MYSQL CONFIGURATION
# ==================================================

DB_CONFIG = {

    "host": "localhost",

    "user": "root",

    "password": "root",

    "database": "student_performance"

}


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_db_connection():

    return mysql.connector.connect(

        host=DB_CONFIG["host"],

        user=DB_CONFIG["user"],

        password=DB_CONFIG["password"],

        database=DB_CONFIG["database"]

    )


# ==================================================
# MACHINE LEARNING MODEL
# ==================================================

data = pd.read_csv(
    "student_data.csv"
)


X = data[
    [
        "attendance",
        "internal_marks",
        "assignment_marks",
        "previous_marks",
        "study_hours"
    ]
]


y = data["result"]


X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=0.2,

    random_state=42

)


model = DecisionTreeClassifier(
    random_state=42
)


model.fit(
    X_train,
    y_train
)


y_pred = model.predict(
    X_test
)


accuracy = accuracy_score(
    y_test,
    y_pred
)


accuracy_percentage = round(
    accuracy * 100,
    2
)


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    if "user_id" in session:

        if session["role"] == "admin":

            return redirect(
                url_for("admin_dashboard")
            )

        return redirect(
            url_for("student_dashboard")
        )

    return redirect(
        url_for("login")
    )


# ==================================================
# LOGIN PAGE
# ==================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip()

        password = request.form["password"]


        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s
            """,
            (email,)
        )


        user = cursor.fetchone()


        cursor.close()

        connection.close()


        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]

            session["name"] = user["name"]

            session["email"] = user["email"]

            session["college_name"] = user[
                "college_name"
            ]

            session["role"] = user["role"]


            if user["role"] == "admin":

                return redirect(
                    url_for(
                        "admin_dashboard"
                    )
                )

            else:

                return redirect(
                    url_for(
                        "student_dashboard"
                    )
                )


        return render_template(
            "login.html",
            error="Invalid email or password."
        )


    return render_template(
        "login.html"
    )


# ==================================================
# SIGNUP
# ==================================================

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    if request.method == "POST":

        name = request.form[
            "name"
        ].strip()


        email = request.form[
            "email"
        ].strip().lower()


        password = request.form[
            "password"
        ]


        confirm_password = request.form[
            "confirm_password"
        ]


        college_name = request.form[
            "college_name"
        ].strip()


        # ------------------------------------------
        # VALIDATION
        # ------------------------------------------

        if not name:

            return render_template(
                "signup.html",
                error="Please enter your name."
            )


        if not email:

            return render_template(
                "signup.html",
                error="Please enter your email."
            )


        if len(password) < 6:

            return render_template(
                "signup.html",
                error=
                "Password must contain at least 6 characters."
            )


        if password != confirm_password:

            return render_template(
                "signup.html",
                error=
                "Passwords do not match."
            )


        if not college_name:

            return render_template(
                "signup.html",
                error=
                "Please enter your college name."
            )


        try:

            connection = get_db_connection()

            cursor = connection.cursor()


            # Check email

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = %s
                """,
                (email,)
            )


            existing_user = cursor.fetchone()


            if existing_user:

                cursor.close()

                connection.close()


                return render_template(
                    "signup.html",
                    error=
                    "Email already registered."
                )


            # --------------------------------------
            # HASH PASSWORD
            # --------------------------------------

            hashed_password = (
                generate_password_hash(
                    password
                )
            )


            # --------------------------------------
            # INSERT USER
            # --------------------------------------

            cursor.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    college_name,
                    role
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    'student'
                )
                """,

                (
                    name,
                    email,
                    hashed_password,
                    college_name
                )
            )


            connection.commit()


            cursor.close()

            connection.close()


            return redirect(
                url_for(
                    "login",
                    registered="1"
                )
            )


        except mysql.connector.Error as error:

            print(
                "Database Error:",
                error
            )


            return render_template(
                "signup.html",
                error=
                "Unable to create account."
            )


    return render_template(
        "signup.html"
    )


# ==================================================
# STUDENT DASHBOARD
# ==================================================

@app.route("/student-dashboard")
def student_dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    if session["role"] != "student":

        return redirect(
            url_for("admin_dashboard")
        )


    return render_template(

        "student_dashboard.html",

        name=session["name"],

        college=session[
            "college_name"
        ],

        accuracy=accuracy_percentage

    )


# ==================================================
# ADMIN DASHBOARD
# ==================================================

@app.route("/admin-dashboard")
def admin_dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    if session["role"] != "admin":

        return redirect(
            url_for("student_dashboard")
        )


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # Total users

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM users
            WHERE role = 'student'
            """
        )

        total_students = cursor.fetchone()[
            "total"
        ]


        # Total predictions

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM students
            """
        )

        total_predictions = cursor.fetchone()[
            "total"
        ]


        # Pass count

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM students
            WHERE prediction = 'Pass'
            """
        )

        total_pass = cursor.fetchone()[
            "total"
        ]


        # Fail count

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM students
            WHERE prediction = 'Fail'
            """
        )

        total_fail = cursor.fetchone()[
            "total"
        ]


        cursor.close()

        connection.close()


        return render_template(

            "admin_dashboard.html",

            name=session["name"],

            total_students=total_students,

            total_predictions=total_predictions,

            total_pass=total_pass,

            total_fail=total_fail,

            accuracy=accuracy_percentage

        )


    except Exception as error:

        print(
            "Dashboard Error:",
            error
        )


        return "Unable to load dashboard."


# ==================================================
# PREDICTION
# ==================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    if "user_id" not in session:

        return jsonify({

            "success": False,

            "message":
            "Please login first."

        })


    try:

        student_name = request.form[
            "student_name"
        ].strip()


        attendance = float(
            request.form["attendance"]
        )


        internal_marks = float(
            request.form[
                "internal_marks"
            ]
        )


        assignment_marks = float(
            request.form[
                "assignment_marks"
            ]
        )


        previous_marks = float(
            request.form[
                "previous_marks"
            ]
        )


        study_hours = float(
            request.form[
                "study_hours"
            ]
        )


        # ------------------------------------------
        # VALIDATION
        # ------------------------------------------

        if not student_name:

            return jsonify({

                "success": False,

                "message":
                "Please enter student name."

            })


        if not 0 <= attendance <= 100:

            return jsonify({

                "success": False,

                "message":
                "Attendance must be between 0 and 100."

            })


        if not 0 <= internal_marks <= 100:

            return jsonify({

                "success": False,

                "message":
                "Internal marks must be between 0 and 100."

            })


        if not 0 <= assignment_marks <= 100:

            return jsonify({

                "success": False,

                "message":
                "Assignment marks must be between 0 and 100."

            })


        if not 0 <= previous_marks <= 100:

            return jsonify({

                "success": False,

                "message":
                "Previous marks must be between 0 and 100."

            })


        if not 0 <= study_hours <= 24:

            return jsonify({

                "success": False,

                "message":
                "Study hours must be between 0 and 24."

            })


        # ------------------------------------------
        # CREATE DATA
        # ------------------------------------------

        new_student = pd.DataFrame({

            "attendance": [attendance],

            "internal_marks": [
                internal_marks
            ],

            "assignment_marks": [
                assignment_marks
            ],

            "previous_marks": [
                previous_marks
            ],

            "study_hours": [
                study_hours
            ]

        })


        # ------------------------------------------
        # PREDICTION
        # ------------------------------------------

        prediction = model.predict(
            new_student
        )[0]


        # ------------------------------------------
        # PROBABILITY
        # ------------------------------------------

        probabilities = model.predict_proba(
            new_student
        )[0]


        classes = model.classes_


        probability_dict = {}


        for class_name, probability in zip(
            classes,
            probabilities
        ):

            probability_dict[
                class_name
            ] = round(
                probability * 100,
                2
            )


        predicted_probability = (
            probability_dict.get(
                prediction,
                0
            )
        )


        # ------------------------------------------
        # SAVE TO MYSQL
        # ------------------------------------------

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(

            """
            INSERT INTO students
            (
                user_id,
                student_name,
                attendance,
                internal_marks,
                assignment_marks,
                previous_marks,
                study_hours,
                prediction,
                prediction_probability
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,

            (

                session["user_id"],

                student_name,

                attendance,

                internal_marks,

                assignment_marks,

                previous_marks,

                study_hours,

                prediction,

                predicted_probability

            )

        )


        connection.commit()


        cursor.close()

        connection.close()


        return jsonify({

            "success": True,

            "prediction": prediction,

            "accuracy":
            accuracy_percentage,

            "probabilities":
            probability_dict,

            "student_name":
            student_name

        })


    except Exception as error:

        print(
            "Prediction Error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
            "Unable to make prediction."

        })


# ==================================================
# STUDENT RECORDS
# ADMIN ONLY
# ==================================================

@app.route("/records")
def records():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    if session["role"] != "admin":

        return redirect(
            url_for("student_dashboard")
        )


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                students.*,
                users.email,
                users.college_name
            FROM students
            LEFT JOIN users
                ON students.user_id = users.id
            ORDER BY students.id DESC
            """
        )


        students = cursor.fetchall()


        cursor.close()

        connection.close()


        return render_template(

            "records.html",

            students=students,

            accuracy=accuracy_percentage,

            name=session["name"]

        )


    except Exception as error:

        print(
            "Records Error:",
            error
        )


        return "Unable to load records."


# ==================================================
# DELETE RECORD
# ADMIN ONLY
# ==================================================

@app.route(
    "/delete/<int:student_id>",
    methods=["DELETE"]
)
def delete_student(student_id):

    if "user_id" not in session:

        return jsonify({

            "success": False,

            "message":
            "Please login first."

        })


    if session["role"] != "admin":

        return jsonify({

            "success": False,

            "message":
            "Access denied."

        })


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(

            """
            DELETE FROM students
            WHERE id = %s
            """,

            (student_id,)

        )


        connection.commit()


        cursor.close()

        connection.close()


        return jsonify({

            "success": True,

            "message":
            "Record deleted successfully."

        })


    except Exception as error:

        print(
            "Delete Error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
            "Unable to delete record."

        })


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ==================================================
# CREATE DEFAULT ADMIN
# ==================================================

@app.route("/create-admin")
def create_admin():

    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        email = "admin@gmail.com"

        password = "admin123"


        # Check admin

        cursor.execute(

            """
            SELECT id
            FROM users
            WHERE email = %s
            """,

            (email,)

        )


        existing = cursor.fetchone()


        if existing:

            cursor.close()

            connection.close()


            return """
            <h2>Admin already exists.</h2>
            <p>Email: admin@gmail.com</p>
            """


        hashed_password = (
            generate_password_hash(
                password
            )
        )


        cursor.execute(

            """
            INSERT INTO users
            (
                name,
                email,
                password,
                college_name,
                role
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                'admin'
            )
            """,

            (

                "Administrator",

                email,

                hashed_password,

                "College Administration"

            )

        )


        connection.commit()


        cursor.close()

        connection.close()


        return """
        <h2>Admin created successfully!</h2>

        <p>Email: admin@gmail.com</p>

        <p>Password: admin123</p>

        <br>

        <a href="/login">
        Go to Login
        </a>
        """


    except Exception as error:

        print(
            "Admin Error:",
            error
        )


        return "Unable to create admin."


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    print(
        "======================================"
    )

    print(
        " STUDENT PERFORMANCE PREDICTION"
    )

    print(
        "======================================"
    )

    print(
        "Model Accuracy:",
        accuracy_percentage,
        "%"
    )

    print(
        "Website:"
        " http://127.0.0.1:5000"
    )

    app.run(
        debug=True
    )
