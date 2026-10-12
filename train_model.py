
import pandas as pd
from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

DATA_PATH = Path("data/WELFake_Dataset.csv")
MODEL_PATH = Path("truthlens_model.pkl")

print("Loading dataset...")
df = pd.read_csv(DATA_PATH)

# Keep only the columns we need and remove missing values
df = df[["text", "label"]].dropna()
df["text"] = df["text"].astype(str).str.strip()
df = df[df["text"] != ""]

X = df["text"]
y = df["label"].astype(int)

print("Total articles:", len(df))
print("\nSplitting data into training and testing sets...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training articles:", len(X_train))
print("Testing articles:", len(X_test))

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        stop_words="english",
        max_features=50000,
        ngram_range=(1, 2),
        min_df=2
    )),
    ("classifier", LogisticRegression(
        max_iter=1000,
        random_state=42
    ))
])

print("\nTraining TruthLens AI model...")
model.fit(X_train, y_train)

print("Testing model...")
predictions = model.predict(X_test)

print("\n===== TRUTHLENS AI RESULTS =====")
print(f"Accuracy:  {accuracy_score(y_test, predictions):.4f}")
print(f"Precision: {precision_score(y_test, predictions, zero_division=0):.4f}")
print(f"Recall:    {recall_score(y_test, predictions, zero_division=0):.4f}")
print(f"F1-score:  {f1_score(y_test, predictions, zero_division=0):.4f}")

print("\nClassification report:")
print(classification_report(y_test, predictions, zero_division=0))

print("Confusion matrix:")
print(confusion_matrix(y_test, predictions))

joblib.dump(model, MODEL_PATH)
print(f"\nModel saved to: {MODEL_PATH}")
print("Training and evaluation completed!")
