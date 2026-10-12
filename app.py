
import streamlit as st
import joblib
from pathlib import Path

MODEL_PATH = Path("truthlens_model.pkl")

st.set_page_config(
    page_title="TruthLens AI",
    page_icon="🔎",
    layout="centered"
)

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

st.title("🔎 TruthLens AI")
st.subheader("AI-powered News Classification")
st.write(
    "Paste a news article below to see whether its writing patterns "
    "resemble the REAL or FAKE examples in our training dataset."
)

st.warning(
    "This is an experimental ML classifier, not a fact-checking service. "
    "Its prediction can be wrong and does not prove whether a claim is true."
)

article = st.text_area(
    "Paste a news article",
    height=220,
    placeholder="Paste the article text here..."
)

if st.button("Analyze Article", type="primary"):
    if len(article.strip()) < 50:
        st.error("Please enter a longer article (at least 50 characters).")
    else:
        try:
            model = load_model()
            prediction = int(model.predict([article])[0])
            probabilities = model.predict_proba([article])[0]
            confidence = float(max(probabilities)) * 100

            if prediction == 1:
                st.error("Prediction: FAKE-like")
            else:
                st.success("Prediction: REAL-like")

            st.metric("Model confidence", f"{confidence:.1f}%")
            st.caption(
                "Confidence reflects the model's class probabilities, "
                "not the probability that the article is factually true."
            )
        except Exception as e:
            st.error(f"Could not analyze the article: {e}")

st.divider()
st.caption("TruthLens AI | SDG 16: Peace, Justice and Strong Institutions")
