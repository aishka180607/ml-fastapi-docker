import pandas as pd
import joblib
import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("bird-strike-prediction")

data = pd.read_csv("birds.csv", keep_default_na=False, na_values=[""])
print("Rows, columns:", data.shape)

data = data[data["effect"].notna()]
data["affected"] = (data["effect"] != "None").astype(int)
print(data["affected"].value_counts())

numeric_cols = ["height", "speed", "ac_mass", "num_engs"]
categorical_cols = ["phase_of_flt", "time_of_day", "sky", "birds_struck"]

data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].median())
data[categorical_cols] = data[categorical_cols].fillna("Unknown")

X = data[numeric_cols + categorical_cols]
y = data["affected"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

preprocessor = ColumnTransformer(transformers=[
    ("num", StandardScaler(), numeric_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols)
])

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=12, class_weight="balanced", random_state=42),
    "Gradient Boosting": HistGradientBoostingClassifier(class_weight="balanced", random_state=42)
}

results = {}

for name, clf in models.items():
    model = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", clf)
    ])

    with mlflow.start_run(run_name=name):
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        mlflow.log_param("model_name", name)
        mlflow.log_params(clf.get_params())

        metrics = {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}
        mlflow.log_metrics(metrics)

        mlflow.sklearn.log_model(model, name="model", input_example=X_train.head(3),
                                 serialization_format="cloudpickle")

    print(f"\n{name}")
    print("Accuracy:", round(accuracy, 3))
    print(classification_report(y_test, y_pred))

    results[name] = metrics

best_name = max(results, key=lambda name: results[name]["f1"])
print("Best model:", best_name, "F1:", round(results[best_name]["f1"], 3))

best_model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", models[best_name])
])
best_model.fit(X_train, y_train)

joblib.dump(best_model, "model.joblib")
print("Model saved to model.joblib")

# best model goes to Model Registry
with mlflow.start_run(run_name=f"Best model - {best_name}"):
    mlflow.log_param("model_name", best_name)
    mlflow.log_params(models[best_name].get_params())
    mlflow.log_metrics(results[best_name])
    mlflow.log_artifact("model.joblib")
    mlflow.sklearn.log_model(
        best_model,
        name="model",
        input_example=X_train.head(3),
        serialization_format="cloudpickle",
        registered_model_name="bird-strike-model"
    )

print("Model registered in MLflow as bird-strike-model")
