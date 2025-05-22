import streamlit as st
import openai
import os
import random
import csv
from datetime import datetime

# --- CONFIG ---
openai.api_key = os.getenv("OPENAI_API_KEY") or "sk-REPLACE_ME"
st.set_page_config(page_title="Explain Like I'm 5", layout="wide")

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
            transition: background-color 0.3s ease;
        }

        .header-logo {
            font-size: 6em;
            font-weight: 900;
            color: white;
            margin: 20px 0 10px 10px;
            transition: all 0.3s ease-in-out;
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
            transition: box-shadow 0.3s ease;
        }

        .tooltip-legend {
            display: flex;
            justify-content: space-between;
            margin-top: -10px;
            margin-bottom: 30px;
            color: white;
        }

        .tooltip-legend span {
            position: relative;
            font-size: 0.95em;
            cursor: help;
            transition: color 0.3s ease;
        }

        .tooltip-legend span:hover {
            color: #ffd700;
        }

        .tooltip-legend span::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 120%;
            left: 50%;
            transform: translateX(-50%);
            background-color: #0077b6;
            color: #fff;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 0.75em;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
            z-index: 999;
        }

        .tooltip-legend span:hover::after {
            opacity: 1;
        }

        button[kind="primary"], .stButton > button {
            transition: all 0.3s ease-in-out;
            border: none;
            box-shadow: 0 0 0px transparent;
            font-weight: bold;
        }

        button[kind="primary"]:hover, .stButton > button:hover {
            box-shadow: 0 0 12px #ffb3ec, 0 0 20px #c6e2ff;
            transform: scale(1.03);
        }

        .typing {
            font-size: 1.2em;
            color: white;
            font-family: monospace;
            overflow: hidden;
            border-right: .1em solid white;
            white-space: nowrap;
            margin: 0 auto;
            animation: typing 1.5s steps(20, end), blink-caret 0.8s step-end infinite;
        }

        @keyframes typing {
            from { width: 0 }
            to { width: 100% }
        }

        @keyframes blink-caret {
            from, to { border-color: transparent }
            50% { border-color: white; }
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('''
<div class="header-logo">
    Explain Like I'm 5
</div>
''', unsafe_allow_html=True)

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

# --- EXAMPLE PROMPTS ---
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

# --- LOG INTERACTIONS ---
def log_interaction(prompt, level_label):
    with open("usage_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), prompt[:50], level_label])

# --- LLM CALL ---
def get_explanation(text, mode_prompt):
    prompt = f"{mode_prompt}\n\nText:\n'''\n{text}\n'''"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're an expert at simplifying complex topics for different audiences."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message["content"].strip()

# --- EXPLAIN BUTTON ---
if st.button("✨ Explain it!"):
    if text_input.strip():
        log_interaction(text_input, EXPLANATION_LEVELS[level][0])
        st.markdown('<div class="typing">Translating brainwaves into plain English...</div>', unsafe_allow_html=True)
        result = get_explanation(text_input, EXPLANATION_LEVELS[level][1])
        st.markdown("### Simplified Explanation:")
        safe_html = result.replace('\n', '<br>')
        st.markdown(f"<div class='explanation-box'>{safe_html}</div>", unsafe_allow_html=True)
    else:
        st.warning("Paste something in first, my guy.")
