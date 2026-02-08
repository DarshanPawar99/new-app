import json
import smtplib
import ssl
from email.message import EmailMessage

import streamlit as st

st.set_page_config(page_title="For Pragya 💘", page_icon="💘", layout="wide")

# -----------------------------
# Content
# -----------------------------
SUBJECT = "Hurray, it’s a date! 💘"
BODY = """Hey Pragya,

I’m so happy you said yes. 💖

I’m really sorry — because of a sudden plan, I won’t be able to take you out on the 14th.
Can we make it 15 Feb instead?

I want to take you on a date and do something you’ve wanted to try for sometime — your choice.
I’m really glad you said yes.

Can’t wait for our date, Winnie 🐻

Love,
Bunnu 🐰
"""

YES_TEXTS = [
    "YES 😍",
    "YES 💘 (do it)",
    "YES 🥹 (trust me)",
    "YES ✨ (worth it)",
    "YES 🫶 (best choice)",
    "YES 🔥 (final answer)",
    "YES 😈 u have no choice Pichuuuu",
    "YES 😈 u have no choice Pichuuuu",
]

NO_TEXTS = [
    "NO 🙈",
    "NO 😬",
    "NO 😶",
    "NO 🤡",
    "NO 😵",
    "NO 🫠",
    "NO 😭",
    "NO ...gone 👻",
]

TINY_NOTES = [
    "no pressure... but yes is elite 😌",
    "Winnie, that YES button looks cute on you",
    "Billu, destiny keeps pointing to YES",
    "Pichuu, this is your main-character moment",
    "every NO powers up YES",
    "NO is literally shrinking now 👀",
    "almost out of NO energy",
    "resistance level = exhausted",
]

HOVER_TAUNTS = [
    "you missed it haahaa 😜",
    "too slowww Winnie 👀",
    "almost, Billu 😂",
    "again missed it hehe 🤭",
]


# -----------------------------
# Email
# -----------------------------
def _to_bool(v, default=True):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in {"1", "true", "yes", "y"}
    return default


def send_mail_from_secrets(subject: str, body: str):
    """
    Requires Streamlit secrets:

    [smtp]
    host = "smtp.gmail.com"
    port = 587
    username = "your@gmail.com"
    password = "16charapppassword"   # no spaces
    from_email = "your@gmail.com"
    to_email = "target@gmail.com"    # or JSON list string
    use_tls = true
    """
    try:
        smtp_cfg = st.secrets["smtp"]
    except Exception:
        return False, "Missing [smtp] in Streamlit secrets."

    host = smtp_cfg.get("host", "smtp.gmail.com")
    port = int(smtp_cfg.get("port", 587))
    username = smtp_cfg.get("username", "").strip()
    password = smtp_cfg.get("password", "").replace(" ", "").strip()  # tolerate accidental spaces
    from_email = smtp_cfg.get("from_email", username).strip()
    use_tls = _to_bool(smtp_cfg.get("use_tls", True), default=True)

    to_raw = smtp_cfg.get("to_email", "")
    if isinstance(to_raw, list):
        to_emails = [str(x).strip() for x in to_raw if str(x).strip()]
    elif isinstance(to_raw, str) and to_raw.strip().startswith("["):
        to_emails = [str(x).strip() for x in json.loads(to_raw) if str(x).strip()]
    elif isinstance(to_raw, str) and to_raw.strip():
        to_emails = [to_raw.strip()]
    else:
        return False, "to_email is missing in secrets."

    if not username or not password:
        return False, "SMTP username/password missing."

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to_emails)
    msg.set_content(body)

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.ehlo()
            if use_tls:
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
            server.login(username, password)
            server.send_message(msg)
        return True, f"Email sent to {', '.join(to_emails)}"
    except smtplib.SMTPAuthenticationError as e:
        return False, f"SMTP auth failed: {e}"
    except Exception as e:
        return False, f"SMTP error: {e}"


# -----------------------------
# Session state
# -----------------------------
defaults = {
    "no_clicks": 0,
    "note_step": 0,
    "swap_count": 0,      # first 4 swaps
    "yes_left": True,
    "accepted": False,
    "mail_sent": False,
    "mail_info": "",
    "last_taunt": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
      [data-testid="stHeader"] {display: none;}
      [data-testid="stToolbar"] {display: none;}

      .stApp{
        background: linear-gradient(-45deg,#ff4d6d,#ff8fa3,#a78bfa,#60a5fa,#34d399,#f59e0b);
        background-size: 400% 400%;
        animation: bgMove 14s ease infinite;
      }

      @keyframes bgMove{
        0%{background-position:0% 50%}
        50%{background-position:100% 50%}
        100%{background-position:0% 50%}
      }

      .block-container{
        max-width: 1100px !important;
        padding-top: 0.4rem !important;
        padding-bottom: 1rem !important;
      }

      .hero-title{
        text-align:center;
        color:#fff;
        font-weight:900;
        font-size: clamp(34px, 4vw, 56px);
        margin: 0 0 8px 0;
        text-shadow: 0 3px 14px rgba(0,0,0,.25);
      }

      .glass-card{
        background: rgba(255,255,255,.20);
        border:1px solid rgba(255,255,255,.34);
        backdrop-filter: blur(8px);
        border-radius: 18px;
        box-shadow: 0 3px 8px rgba(0,0,0,.08);
        padding: 10px;
      }

      .letter{
        background: rgba(255,255,255,.94);
        border-radius: 14px;
        padding: 20px 22px;
        color: #2e2030;
        line-height: 1.58;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,.8);
      }

      .letter h2{
        margin:0 0 10px 0;
        color:#7a1f4f;
        font-size: clamp(24px,2.2vw,34px);
      }

      .letter p{
        margin:0 0 9px 0;
        font-size: 17px;
      }

      .sign{
        margin-top: 10px;
        font-weight: 700;
        color:#6a2148;
        font-size: 17px;
      }

      .status{
        margin-top:12px;
        text-align:center;
        color:#fff;
        font-weight:800;
        font-size: clamp(16px,1.8vw,24px);
        text-shadow: 0 2px 8px rgba(0,0,0,.25);
      }

      .tiny{
        text-align:center;
        color:#000;
        font-size:12px;
        font-weight:700;
        margin-top: 4px;
        background: rgba(255,255,255,.70);
        display:inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        position: relative;
        left: 50%;
        transform: translateX(-50%);
      }

      /* Buttons */
      div[data-testid="stButton"] > button {
        border-radius: 16px !important;
        font-weight: 900 !important;
        border: 0 !important;
        min-height: 52px !important;
      }

      /* Floating hearts */
      .hearts{
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
      }

      .hearts span{
        position: absolute;
        animation: floatUp var(--d) ease-in infinite;
        opacity: .75;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,.15));
        user-select: none;
      }

      @keyframes floatUp{
        0%   { transform: translateY(8vh) scale(.65); opacity: 0; }
        12%  { opacity: .95; }
        90%  { opacity: .75; }
        100% { transform: translateY(-110vh) scale(1.2); opacity: 0; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# hearts background
hearts_html = """
<div class="hearts">
  <span style="left:3%; top:92%; font-size:14px; --d:10s;">💖</span>
  <span style="left:10%; top:98%; font-size:18px; --d:13s;">💘</span>
  <span style="left:18%; top:96%; font-size:12px; --d:9s;">💕</span>
  <span style="left:26%; top:99%; font-size:17px; --d:12s;">💓</span>
  <span style="left:34%; top:95%; font-size:13px; --d:11s;">💗</span>
  <span style="left:42%; top:98%; font-size:20px; --d:14s;">💝</span>
  <span style="left:50%; top:97%; font-size:15px; --d:10.5s;">🫶</span>
  <span style="left:58%; top:99%; font-size:16px; --d:12.5s;">💞</span>
  <span style="left:66%; top:96%; font-size:13px; --d:9.5s;">💖</span>
  <span style="left:74%; top:98%; font-size:19px; --d:13.5s;">💘</span>
  <span style="left:82%; top:95%; font-size:14px; --d:11.5s;">💕</span>
  <span style="left:90%; top:97%; font-size:18px; --d:12s;">💗</span>
  <span style="left:96%; top:99%; font-size:12px; --d:9.8s;">💓</span>
</div>
"""
st.markdown(hearts_html, unsafe_allow_html=True)

# -----------------------------
# Header + Letter
# -----------------------------
st.markdown('<div class="hero-title">Will you be my Valentine, Pragya? 💘</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="glass-card">
      <div class="letter">
        <h2>Hey Pragya,</h2>
        <p>I’ll keep this simple — you’re genuinely amazing.
        Your big bright eyes, your beautiful voice, and your goated personality... all of it is unreal.
        Even your cute anger (that wannabe toxic mode 😌) is somehow adorable.</p>

        <p>You make me feel calm and relaxed, like the whole world goes quiet.
        The warmth of your hand, your tight hugs, and the fragrance of your hair... uff.
        Everything about you makes me go a little crazy (in the best way).</p>

        <p>Bonus points: you’re funny, cute, smart, diligent, and hot.
        How is all that in one person?
        Also yes — my favorite thing is your nose XD.</p>

        <p>I’d be the luckiest guy if I could make you mine forever.</p>

        <div class="sign">— Yours, hoping for a YES 💌</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Status text
# -----------------------------
no_clicks = st.session_state.no_clicks
note_step = min(st.session_state.note_step, len(TINY_NOTES) - 1)
yes_label = YES_TEXTS[min(no_clicks, len(YES_TEXTS) - 1)]
no_label = NO_TEXTS[min(no_clicks, len(NO_TEXTS) - 1)]

if st.session_state.accepted:
    status_text = "You chose YES. Best decision ever 🤝💖"
    tiny_text = "she said YES and my heart did cartwheels"
elif no_clicks >= 7:
    status_text = "NO vanished... looks like fate picked YES 😌"
    tiny_text = "resistance level = exhausted"
elif no_clicks < 4:
    status_text = "Pick one, Winnie 😏"
    tiny_text = st.session_state.last_taunt or TINY_NOTES[note_step]
else:
    status_text = "Every NO just makes YES stronger 💪💘"
    tiny_text = st.session_state.last_taunt or TINY_NOTES[note_step]

st.markdown(f'<div class="status">{status_text}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="tiny">{tiny_text}</div>', unsafe_allow_html=True)
st.write("")

# -----------------------------
# Buttons (native Streamlit -> reliable mail sending)
# -----------------------------
yes_clicked = False
no_clicked = False

# yes grows, no shrinks by layout ratio
yes_w = min(9, 3 + no_clicks)      # grows
no_w = max(1, 7 - no_clicks)       # shrinks

if st.session_state.accepted or no_clicks >= 7:
    c1, c2, c3 = st.columns([1, 3, 1])
    with c2:
        yes_clicked = st.button(yes_label, key="yes_btn", type="primary", use_container_width=True)
else:
    # first 4 "movement" swaps position each NO click
    left_is_yes = st.session_state.yes_left

    if left_is_yes:
        c_left, c_right = st.columns([yes_w, no_w])
        with c_left:
            yes_clicked = st.button(yes_label, key="yes_btn", type="primary", use_container_width=True)
        with c_right:
            no_clicked = st.button(no_label, key="no_btn", use_container_width=True)
    else:
        c_left, c_right = st.columns([no_w, yes_w])
        with c_left:
            no_clicked = st.button(no_label, key="no_btn", use_container_width=True)
        with c_right:
            yes_clicked = st.button(yes_label, key="yes_btn", type="primary", use_container_width=True)

# -----------------------------
# Click actions
# -----------------------------
if no_clicked and not st.session_state.accepted:
    st.session_state.no_clicks = min(7, st.session_state.no_clicks + 1)
    st.session_state.note_step = min(len(TINY_NOTES) - 1, st.session_state.note_step + 1)

    # swap first 4 times (hover-like movement simulation)
    if st.session_state.swap_count < 4:
        st.session_state.yes_left = not st.session_state.yes_left
        st.session_state.last_taunt = HOVER_TAUNTS[st.session_state.swap_count]
        st.session_state.swap_count += 1
    else:
        st.session_state.last_taunt = ""

    st.rerun()

if yes_clicked:
    st.session_state.accepted = True
    st.session_state.last_taunt = ""

    if not st.session_state.mail_sent:
        ok, info = send_mail_from_secrets(SUBJECT, BODY)
        st.session_state.mail_sent = ok
        st.session_state.mail_info = info

    st.balloons()
    st.rerun()

# -----------------------------
# Mail result info
# -----------------------------
if st.session_state.accepted:
    if st.session_state.mail_sent:
        st.success("Yay! Email sent successfully 💌")
    elif st.session_state.mail_info:
        st.error(f"Could not send email: {st.session_state.mail_info}")
