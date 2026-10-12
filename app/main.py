"""FastAPI service that serves the sentiment model."""
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
import joblib

app = FastAPI(title="Sentiment Serving API", version="1.0.0")

# Load the trained model once, when the app starts up
model = joblib.load("app/model.joblib")

# Expose Prometheus metrics at /metrics (request counts, latency, etc.)
Instrumentator().instrument(app).expose(app)


class PredictRequest(BaseModel):
    text: str


@app.get("/healthz")
def health():
    """Liveness/readiness probe target."""
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    """Take text, return sentiment + confidence."""
    prediction = model.predict([req.text])[0]
    proba = model.predict_proba([req.text])[0].max()
    sentiment = "positive" if prediction == 1 else "negative"
    return {"sentiment": sentiment, "confidence": round(float(proba), 3)}
