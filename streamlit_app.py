import streamlit as st
from openai import OpenAI
import random
from datetime import datetime
from google.oauth2 import service_account
import gspread

# --- CONFIG ---
st.set_page_config(page_title="Explain Like I'm 5", layout="wide")

# --- OPENAI SETUP ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- GOOGLE SHEETS AUTH ---
sheet = None
try:
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=scope
    )
    gc = gspread.authorize(creds)
    sheet = gc.open("ExplainLikeIm5-Logs").sheet1  # or use .worksheet("SheetName") if renamed
except Exception as e:
    st.warning(f"⚠️ Logging to Google Sheets failed: {e}")

# --- STYLES ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@500;700&display=swap" rel="stylesheet">
<style>
    html, body {
        background-color: transparent;
        font-family: 'Quicksand', sans-serif;
    }
    .stApp {
        background-image: url("/mnt/data/2025-05-21T21-59-32.761Z.png");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }
    .header-o {
        font-size: 6em;
        font-weight: 900;
        color: white;
        margin: 20px 0 10px 10px;
    }
    .explanation-box {
        background-color: rgba(0, 0, 0, 0.6);
        padding: 1em;
        border-radius: 10px;
        border: 2px solid #add8e6;
        color: #fff;
        font-size: 1.2em;
        max-height: 400px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="header-logo">Explain Like I\'m 5</div>', unsafe_allow_html=True)
st.caption("Simplify complicated ideas into plain language for any brain level.")

# --- EXPLANATION LEVEL SLIDER ---
EXPLANATION_LEVELS = {
    1: ("I'm 5", "Explain the following text like I'm 5 years old. Use very simple words and short sentences."),
    2: ("Middle School", "Explain the following text to a middle school student. Be clear, fun, and educational."),
    3: ("High School", "Explain the following text to a high school student. Keep it casual but detailed."),
    4: ("College", "Explain the following text to a college student. Use technical language, but keep it understandable."),
    5: ("Intern", "Explain the following text to a new intern in the field. Be professional and detailed.")
}
level = st.slider("Choose your understanding level:", 1, 5, 1, format="%d")

# --- TOOLTIP LEGEND ---
st.markdown("""
<div class="tooltip-legend">
  <span data-tooltip="Super simple words and examples. No jargon.">1: I'm 5</span>
  <span data-tooltip="Middle school level — basic understanding, light detail.">2: Middle School</span>
  <span data-tooltip="High school level — more precise, but still casual.">3: High School</span>
  <span data-tooltip="College level — technical, but still readable.">4: College</span>
  <span data-tooltip="Intern level — assume base knowledge, go deeper.">5: Intern</span>
</div>
""", unsafe_allow_html=True)

# --- EXAMPLES ---
EXAMPLES = [
    "What is quantum computing?",
    "How does the internet work?",
    "Explain inflation in simple terms.",
    "What is blockchain technology?",
    "Why do planes fly?"
]
if st.button("🎲 Load Example Text"):
    st.session_state.example = random.choice(EXAMPLES)
    st.rerun()

text_input = st.text_area("Paste your complicated text here:", value=st.session_state.get("example", ""), height=200)

# --- EXPLAIN FUNCTION ---
def get_explanation(text, mode_prompt):
    prompt = f"{mode_prompt}\n\nText:\n'''\n{text}\n'''"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're an expert at simplifying complex topics for different audiences."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()

# --- EXPLAIN BUTTON ---
if st.button("✨ Explain it!"):
    if text_input.strip():
        st.markdown('<div class="typing">Translating brainwaves into plain English...</div>', unsafe_allow_html=True)
        result = get_explanation(text_input, EXPLANATION_LEVELS[level][1])
        st.markdown("### Simplified Explanation:")
        safe_html = result.replace('\n', '<br>')
        st.markdown(f"<div class='explanation-box'>{safe_html}</div>", unsafe_allow_html=True)

        log_row = [
            datetime.now().isoformat(),
            EXPLANATION_LEVELS[level][0],
            text_input
        ]
        st.write("🔍 Attempting to log:", log_row)

        if sheet:
            try:
                sheet.append_row(log_row)
                st.success("✅ Logged to Google Sheets!")
            except Exception as e:
                st.warning(f"⚠️ Failed to log result: {e}")
    else:
        st.warning("Paste something in first, my guy.")

# --- TEST BUTTON FOR LOGGING ---
if st.button("🧪 Test Logging"):
    try:
        test_row = ["Test Time", "Test Level", "Test Input"]
        sheet.append_row(test_row)
        st.success("✅ Test row successfully logged.")
    except Exception as e:
        st.error(f"❌ Manual test log failed: {e}")
