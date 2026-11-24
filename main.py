import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Bird Strike API")

model = joblib.load("model.joblib")


class BirdStrike(BaseModel):
    height: float
    speed: float
    ac_mass: int
    num_engs: int
    phase_of_flt: str
    time_of_day: str
    sky: str
    birds_struck: str

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "height": 500,
                "speed": 140,
                "ac_mass": 4,
                "num_engs": 2,
                "phase_of_flt": "Take-off run",
                "time_of_day": "Day",
                "sky": "No Cloud",
                "birds_struck": "11-100"
            }]
        }
    }


@app.get("/")
def root():
    return {"message": "ML API is running"}


@app.post("/predict")
def predict(data: BirdStrike):
    df = pd.DataFrame([data.model_dump()])

    prediction = int(model.predict(df)[0])
    probability = float(model.predict_proba(df)[0][1])

    return {
        "prediction": prediction,
        "result": "affected" if prediction == 1 else "not affected",
        "probability": round(probability, 3)
    }
