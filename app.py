
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

st.markdown("<h1 style='text-align:center;'>🔎 TruthLens AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;font-size:20px;'>Smarter Checks. Safer News.</p>", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: linear-gradient(135deg, #f8f7ff 0%, #ffffff 55%, #f0f4ff 100%);
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1000px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

h1 {
    color: #172554;
    font-weight: 800 !important;
    letter-spacing: -1.5px;
}

h1, h2, h3, p, label,
.stMarkdown, .stMarkdown p,
.stTextInput label, .stTextArea label,
.stTabs [data-baseweb="tab"] {
    color: #26365d !important;
}
{
    color: #26365d;
}

.stButton > button {
    background: linear-gradient(90deg, #6965f5, #8980ff);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1.2rem;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #514bdc, #7165ee);
    color: white;
    border: none;
    transform: translateY(-2px);
}

.stTextInput input,
.stTextArea textarea,
.stTextInput input[type="email"],
.stTextInput input[type="password"] {
    color: #172554 !important;
    background-color: #ffffff !important;
    border: 1px solid #deddf5;
    border-radius: 12px;
    -webkit-text-fill-color: #172554 !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #7771f5;
    box-shadow: 0 0 0 2px #e7e5ff;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    border-bottom: 1px solid #e7e7f5;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
    padding: 10px 20px;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e7e7f5;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 5px 20px rgba(68, 63, 150, 0.06);
}

div[data-testid="stForm"] {
    background: white;
    padding: 22px;
    border: 1px solid #e7e7f5;
    border-radius: 16px;
}

hr {
    border-color: #e6e5f5;
}
</style>
""", unsafe_allow_html=True)


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


st.markdown("### 📰 Analyze a News Article")
st.caption("Paste the article below and let AI analyze its writing patterns.")

article = st.text_area(
    "Article text",
    height=250,
    placeholder="Paste your news article here...",
    label_visibility="collapsed"
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
                st.markdown(
                    "<div style='background:#fff0f0;padding:20px;border-radius:15px;"
                    "border:1px solid #ffcaca;color:#a52222;font-size:22px;"
                    "font-weight:700;'>⚠️ FAKE-like</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    "<div style='background:#eafaf1;padding:20px;border-radius:15px;"
                    "border:1px solid #b9ebce;color:#167344;font-size:22px;"
                    "font-weight:700;'>✓ REAL-like</div>",
                    unsafe_allow_html=True
                )


            

            st.markdown("### 📊 Analysis Confidence")
            st.progress(min(confidence / 100, 1.0))
            st.markdown(
                f"<p style='font-size:24px;font-weight:700;color:#6965f5;'>{confidence:.1f}%</p>",
                unsafe_allow_html=True
            )
            st.caption(
                "Confidence reflects the model's class probabilities, "
                "not the probability that the article is factually true."
            )
        except Exception as e:
            st.error(f"Could not analyze the article: {e}")



st.divider()
st.markdown(
    """
    <div style="text-align:center;padding:15px 0;color:#77769a;">
        <p style="font-size:16px;font-weight:600;color:#514bdc;">
            🔎 TruthLens AI
        </p>
        <p>Think critically. Read responsibly.</p>
        <p style="font-size:12px;">
            SDG 16 · Peace, Justice and Strong Institutions
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
