# Bird Strike Prediction API

In this project I trained a machine learning model and deployed it as an API using FastAPI and Docker (Practical Task 6). In SIS-3 I extended it with a Streamlit frontend and MLflow for experiment tracking and model registry.

## About the project

The model predicts if a bird strike affected the flight or not. Affected means that after the strike there was precautionary landing, aborted take-off, engine shut down or other effect.

I used the FAA Wildlife Strike dataset (birds dataset from OpenIntro). It has 19302 bird strike reports. I removed rows where effect is unknown, so 13584 rows were left:

1. 0 - not affected (11611 rows)
2. 1 - affected (1973 rows)

Only about 15% of flights were affected, so classes are imbalanced. Because of this I used `class_weight="balanced"` in all models.

## Features

1. `height` - height of the aircraft in feet (0 - 32500)
2. `speed` - speed in knots (0 - 400)
3. `ac_mass` - aircraft mass class (1 - 5)
4. `num_engs` - number of engines (1 - 4)
5. `phase_of_flt` - phase of flight (Take-off run, Climb, En Route, Descent, Approach, Landing Roll, Taxi, Parked)
6. `time_of_day` - Day, Night, Dawn or Dusk
7. `sky` - No Cloud, Some Cloud or Overcast
8. `birds_struck` - how many birds were struck (0, 1, 2-10, 11-100, Over 100)

## Model

First I filled missing values: numeric columns with median and categorical columns with "Unknown". Then numeric columns are scaled with StandardScaler and categorical columns are encoded with OneHotEncoder.

I trained 3 models and compared them on test set (20% of data):

| Model | Accuracy | Recall (affected) | F1 (affected) |
|---|---|---|---|
| Logistic Regression | 0.735 | 0.77 | 0.46 |
| Random Forest | 0.769 | 0.72 | 0.48 |
| Gradient Boosting | 0.767 | 0.78 | 0.49 |

The best model by F1 is Gradient Boosting, so it is saved in `model.joblib` together with preprocessing.

## Project structure

1. `train.py` - trains the models, logs them to MLflow and saves the best one
2. `main.py` - FastAPI app
3. `app.py` - Streamlit frontend
4. `.streamlit/config.toml` - theme colors for Streamlit
5. `model.joblib` - saved model
6. `birds.csv` - dataset
7. `requirements.txt` - libraries
8. `Dockerfile` - instructions for Docker image
9. `README.md` - this file

## How to run locally

1. Create and activate virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```
2. Install libraries:
```
pip install -r requirements.txt
```
3. Train the model:
```
python train.py
```
4. Run the API:
```
uvicorn main:app --reload
```
5. Open in browser http://127.0.0.1:8000/ and http://127.0.0.1:8000/docs

## MLflow (SIS-3)

`train.py` uses MLflow to track experiments:

1. Experiment name: `bird-strike-prediction`
2. Every model (Logistic Regression, Random Forest, Gradient Boosting) is logged as a separate run
3. For each run I log:
   1. parameters - model name and all hyperparameters of the model
   2. metrics - accuracy, precision, recall, F1
   3. artifact - the trained model
4. The best model (Gradient Boosting) is logged in a separate run with `model.joblib` file and registered in the Model Registry as `bird-strike-model`. Every time `train.py` is run a new version is created (version 1, 2, 3...)

MLflow data is saved in `mlflow.db` (SQLite) and `mlruns/` folder.

To open MLflow UI:
```
mlflow ui --backend-store-uri sqlite:///mlflow.db
```
Then open http://127.0.0.1:5000. In "Experiments" you can compare runs and in "Models" you can see the registered model and its versions.

## Streamlit frontend (SIS-3)

`app.py` is a web page in pastel aviation style where user can describe the flight and get prediction. The sidebar looks like a boarding pass and shows model info and the current model version from MLflow Registry. Streamlit does not use the model directly, it sends request to FastAPI `/predict` endpoint and shows the result.

1. Start the API in the first terminal:
```
uvicorn main:app --reload
```
2. Start Streamlit in the second terminal:
```
streamlit run app.py
```
3. Open http://localhost:8501, fill the form and press "Predict"

So the full system is: Streamlit (frontend) → FastAPI (API) → model, and MLflow is used for training and model management.

## How to run with Docker

1. Build the image:
```
docker build -t bird-strike-api .
```
2. Run the container:
```
docker run -d -p 8000:8000 --name bird-strike-api bird-strike-api
```
3. Open http://localhost:8000/docs
4. To stop the container:
```
docker stop bird-strike-api
docker rm bird-strike-api
```

## Endpoints

1. `GET /` - checks that API is running

Response:
```
{"message": "ML API is running"}
```

2. `POST /predict` - returns prediction

Example 1 (take-off, many birds):
```
{
  "height": 500,
  "speed": 140,
  "ac_mass": 4,
  "num_engs": 2,
  "phase_of_flt": "Take-off run",
  "time_of_day": "Day",
  "sky": "No Cloud",
  "birds_struck": "11-100"
}
```
Response:
```
{"prediction": 1, "result": "affected", "probability": 0.819}
```

Example 2 (descent at night, one bird):
```
{
  "height": 3000,
  "speed": 250,
  "ac_mass": 4,
  "num_engs": 2,
  "phase_of_flt": "Descent",
  "time_of_day": "Night",
  "sky": "Overcast",
  "birds_struck": "1"
}
```
Response:
```
{"prediction": 0, "result": "not affected", "probability": 0.06}
```

Probability shows the chance that the flight was affected.
