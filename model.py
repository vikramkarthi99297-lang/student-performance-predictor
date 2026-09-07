import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score


# ============================================
# LOAD DATASET
# ============================================

data = pd.read_csv("student_data.csv")


# ============================================
# INPUT FEATURES
# ============================================

X = data[
    [
        "attendance",
        "internal_marks",
        "assignment_marks",
        "previous_marks",
        "study_hours"
    ]
]


# ============================================
# TARGET
# ============================================

y = data["result"]


# ============================================
# SPLIT DATA
# ============================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# ============================================
# CREATE MODEL
# ============================================

model = DecisionTreeClassifier(
    random_state=42
)


# ============================================
# TRAIN MODEL
# ============================================

model.fit(X_train, y_train)


# ============================================
# TEST MODEL
# ============================================

y_pred = model.predict(X_test)


# ============================================
# ACCURACY
# ============================================

accuracy = accuracy_score(y_test, y_pred)

print("Model trained successfully!")
print("Model Accuracy:", round(accuracy * 100, 2), "%")