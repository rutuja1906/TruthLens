
import streamlit as st
import joblib
import requests
from pathlib import Path

MODEL_PATH = Path("truthlens_model.pkl")
FIREBASE_API_KEY = st.secrets["firebase"]["api_key"]

SIGNUP_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
    f"?key={FIREBASE_API_KEY}"
)
LOGIN_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    f"?key={FIREBASE_API_KEY}"
)

st.set_page_config(
    page_title="TruthLens AI",
    page_icon="🔎",
    layout="centered"
)


def firebase_auth(url, email, password):
    try:
        response = requests.post(
            url,
            json={
                "email": email,
                "password": password,
                "returnSecureToken": True
            },
            timeout=15
        )
        data = response.json()

        if response.ok:
            return data, None

        error_code = data.get("error", {}).get("message", "UNKNOWN_ERROR")
        messages = {
            "EMAIL_EXISTS": "This email is already registered. Please log in.",
            "INVALID_LOGIN_CREDENTIALS": "Incorrect email or password.",
            "INVALID_EMAIL": "Please enter a valid email address.",
            "WEAK_PASSWORD": "Password must be at least 6 characters.",
            "MISSING_PASSWORD": "Please enter your password.",
            "USER_DISABLED": "This account has been disabled.",
            "TOO_MANY_ATTEMPTS_TRY_LATER":
                "Too many attempts. Please try again later."
        }
        return None, messages.get(
            error_code,
            f"Authentication failed: {error_code}"
        )

    except requests.RequestException:
        return None, "Connection failed. Please check your internet and try again."


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


st.title("🔎 TruthLens AI")
st.subheader("AI-powered News Classification")

# LOGIN / REGISTER
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if not st.session_state.user_email:
    st.write("Log in or create an account to use TruthLens AI.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )
            login_submit = st.form_submit_button(
                "Login",
                type="primary"
            )

        if login_submit:
            if not login_email.strip() or not login_password:
                st.error("Please enter your email and password.")
            else:
                result, error = firebase_auth(
                    LOGIN_URL,
                    login_email.strip(),
                    login_password
                )
                if error:
                    st.error(error)
                else:
                    st.session_state.user_email = result["email"]
                    st.session_state.id_token = result["idToken"]
                    st.rerun()

    with register_tab:
        with st.form("register_form"):
            register_email = st.text_input(
                "Email",
                key="register_email"
            )
            register_password = st.text_input(
                "Create password (at least 6 characters)",
                type="password",
                key="register_password"
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="confirm_password"
            )
            register_submit = st.form_submit_button(
                "Create account",
                type="primary"
            )

        if register_submit:
            if not register_email.strip() or not register_password:
                st.error("Please enter an email and password.")
            elif register_password != confirm_password:
                st.error("Passwords do not match.")
            elif len(register_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                result, error = firebase_auth(
                    SIGNUP_URL,
                    register_email.strip(),
                    register_password
                )
                if error:
                    st.error(error)
                else:
                    st.session_state.user_email = result["email"]
                    st.session_state.id_token = result["idToken"]
                    st.rerun()

    st.stop()

# LOGGED-IN APP
st.success(f"Logged in as {st.session_state.user_email}")

if st.button("Logout"):
    st.session_state.user_email = None
    st.session_state.pop("id_token", None)
    st.rerun()

st.divider()

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
