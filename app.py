from flask import Flask, render_template, request, jsonify
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)


# =========================================================
# LOAD DATASET
# =========================================================

data = pd.read_csv("student_data.csv")


# =========================================================
# SELECT FEATURES
# =========================================================

X = data[
    [
        "attendance",
        "internal_marks",
        "assignment_marks",
        "previous_marks",
        "study_hours"
    ]
]


# =========================================================
# TARGET VARIABLE
# =========================================================

y = data["result"]


# =========================================================
# SPLIT DATA
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# =========================================================
# CREATE MACHINE LEARNING MODEL
# =========================================================

model = DecisionTreeClassifier(
    random_state=42
)


# =========================================================
# TRAIN MODEL
# =========================================================

model.fit(X_train, y_train)


# =========================================================
# TEST MODEL
# =========================================================

y_pred = model.predict(X_test)


# =========================================================
# CALCULATE ACCURACY
# =========================================================

accuracy = accuracy_score(y_test, y_pred)

accuracy_percentage = round(accuracy * 100, 2)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        accuracy=accuracy_percentage
    )


# =========================================================
# PREDICTION API
# =========================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # ---------------------------------------------
        # GET DATA FROM WEBSITE
        # ---------------------------------------------

        attendance = float(request.form["attendance"])

        internal_marks = float(
            request.form["internal_marks"]
        )

        assignment_marks = float(
            request.form["assignment_marks"]
        )

        previous_marks = float(
            request.form["previous_marks"]
        )

        study_hours = float(
            request.form["study_hours"]
        )


        # ---------------------------------------------
        # VALIDATION
        # ---------------------------------------------

        if attendance < 0 or attendance > 100:

            return jsonify({
                "success": False,
                "message": "Attendance must be between 0 and 100."
            })


        if internal_marks < 0 or internal_marks > 100:

            return jsonify({
                "success": False,
                "message": "Internal marks must be between 0 and 100."
            })


        if assignment_marks < 0 or assignment_marks > 100:

            return jsonify({
                "success": False,
                "message": "Assignment marks must be between 0 and 100."
            })


        if previous_marks < 0 or previous_marks > 100:

            return jsonify({
                "success": False,
                "message": "Previous marks must be between 0 and 100."
            })


        if study_hours < 0:

            return jsonify({
                "success": False,
                "message": "Study hours cannot be negative."
            })


        # ---------------------------------------------
        # CREATE NEW STUDENT DATA
        # ---------------------------------------------

        new_student = pd.DataFrame({
            "attendance": [attendance],
            "internal_marks": [internal_marks],
            "assignment_marks": [assignment_marks],
            "previous_marks": [previous_marks],
            "study_hours": [study_hours]
        })


        # ---------------------------------------------
        # PREDICT RESULT
        # ---------------------------------------------

        prediction = model.predict(new_student)[0]


        # ---------------------------------------------
        # PREDICTION PROBABILITY
        # ---------------------------------------------

        probabilities = model.predict_proba(new_student)[0]

        class_names = model.classes_

        probability_dict = {}

        for class_name, probability in zip(
            class_names,
            probabilities
        ):
            probability_dict[class_name] = round(
                probability * 100,
                2
            )


        # ---------------------------------------------
        # SEND RESPONSE
        # ---------------------------------------------

        return jsonify({

            "success": True,

            "prediction": prediction,

            "accuracy": accuracy_percentage,

            "probabilities": probability_dict,

            "student": {

                "attendance": attendance,

                "internal_marks": internal_marks,

                "assignment_marks": assignment_marks,

                "previous_marks": previous_marks,

                "study_hours": study_hours

            }

        })


    except Exception as error:

        return jsonify({

            "success": False,

            "message": "Something went wrong. Please check your input."

        })


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print("========================================")
    print(" STUDENT PERFORMANCE PREDICTION SYSTEM")
    print("========================================")

    print(
        "Model Accuracy:",
        accuracy_percentage,
        "%"
    )

    print(
        "Server running at: http://127.0.0.1:5000"
    )

    app.run(
        debug=True
    )