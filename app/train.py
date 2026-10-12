"""Train a tiny sentiment classifier and save it to disk."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

# Tiny labeled dataset: 1 = positive, 0 = negative
texts = [
    "I love this", "this is great", "absolutely fantastic", "so happy with it",
    "best decision ever", "highly recommend", "wonderful experience", "really good",
    "I hate this", "this is terrible", "absolutely awful", "so disappointed",
    "worst decision ever", "do not recommend", "horrible experience", "really bad",
]
labels = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]

# A pipeline = text-to-numbers step + classifier, bundled as one object
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", LogisticRegression()),
])
model.fit(texts, labels)

joblib.dump(model, "app/model.joblib")
print("Model trained and saved to app/model.joblib")
