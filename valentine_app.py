import json
import smtplib
import ssl
from email.message import EmailMessage

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="For Pragya 💘", page_icon="💘", layout="wide")


# -----------------------------
# Email content
# -----------------------------
def get_email_content():
    subject = "Hurray, it’s a date! 💘"
    body = """Hey Pragya,

I’m so happy you said yes. 💖

I’m really sorry — because of a sudden plan, I won’t be able to take you out on the 14th.
Can we make it 15 Feb instead?

I want to take you on a date and do something you’ve wanted to try for sometime — your choice.
I’m really glad you said yes.

Can’t wait for our date, Winnie 🐻

Love,
Bunnu 🐰
"""
    return subject, body


def _to_bool(v, default=True):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in {"1", "true", "yes", "y"}
    return default


def _qp_get(name: str, default: str = "") -> str:
    """Safe query-param getter across Streamlit versions."""
    try:
        val = st.query_params.get(name, default)
        if isinstance(val, list):
            return val[0] if val else default
        return str(val)
    except Exception:
        return default


def send_mail_from_secrets(subject: str, body: str):
    """
    Expects Streamlit secrets:

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
    username = smtp_cfg.get("username", "")
    password = smtp_cfg.get("password", "")
    from_email = smtp_cfg.get("from_email", username)
    use_tls = _to_bool(smtp_cfg.get("use_tls", True), default=True)

    to_raw = smtp_cfg.get("to_email", "")
    if isinstance(to_raw, list):
        to_emails = to_raw
    elif isinstance(to_raw, str) and to_raw.strip().startswith("["):
        to_emails = json.loads(to_raw)
    elif isinstance(to_raw, str) and to_raw.strip():
        to_emails = [to_raw.strip()]
    else:
        return False, "to_email is missing in secrets."

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
        return False, f"SMTP auth failed (check App Password / 2FA): {e}"
    except Exception as e:
        return False, f"SMTP error: {e}"


# -----------------------------
# Global style
# -----------------------------
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    [data-testid="stToolbar"] {display: none;}

    .stApp {
        background: linear-gradient(-45deg,#ff4d6d,#ff8fa3,#a78bfa,#60a5fa,#34d399,#f59e0b);
        background-size: 400% 400%;
        animation: appBgMove 14s ease infinite;
    }

    @keyframes appBgMove{
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    .block-container{
        max-width: 100% !important;
        padding-top: 0.2rem !important;
        padding-bottom: 0.4rem !important;
    }

    iframe[title="streamlit_components.v1.html"]{
        border: none !important;
        border-radius: 12px !important;
        background: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Send email if YES redirect params are present
# -----------------------------
if "sent_tokens" not in st.session_state:
    st.session_state.sent_tokens = set()

send_mail_flag = _qp_get("send_mail", "")
mail_token = _qp_get("mail_token", "")

if send_mail_flag == "1" and mail_token and mail_token not in st.session_state.sent_tokens:
    subject, body = get_email_content()
    ok, info = send_mail_from_secrets(subject, body)

    if ok:
        st.balloons()
        st.success("Yay! Email sent successfully 💌")
    else:
        st.error(f"Could not send email: {info}")

    st.session_state.sent_tokens.add(mail_token)
    try:
        st.query_params.clear()
    except Exception:
        pass


# -----------------------------
# Interactive UI
# -----------------------------
html = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root{
      --yesScale: 1;
      --noScale: 1;
    }

    * { box-sizing: border-box; }

    body{
      margin:0;
      font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      background: transparent;
      min-height: 100vh;
      padding: 12px 10px 10px;
      display:flex;
      align-items:flex-start;
      justify-content:center;
      overflow-x: hidden;
    }

    .bg-hearts{
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: 0;
      overflow: hidden;
    }

    .bg-heart{
      position: absolute;
      opacity: 0;
      animation: heartFade var(--dur, 2800ms) ease-in-out forwards;
      filter: drop-shadow(0 2px 4px rgba(0,0,0,.12));
      user-select: none;
      will-change: transform, opacity;
    }

    @keyframes heartFade{
      0%   { transform: translateY(8px) scale(.6); opacity: 0; }
      12%  { opacity: .95; }
      70%  { opacity: .78; }
      100% { transform: translateY(-20px) scale(1.15); opacity: 0; }
    }

    .wrap{
      width:min(1140px, 92vw);
      position: relative;
      z-index: 2;
      margin-top: 2px;
    }

    .hero{
      text-align:center;
      color:#fff;
      font-weight:900;
      font-size: clamp(34px, 4vw, 58px);
      text-shadow:0 3px 12px rgba(0,0,0,.20);
      margin: 0 0 8px;
    }

    .card{
      background: rgba(255,255,255,.20);
      border:1px solid rgba(255,255,255,.32);
      backdrop-filter: blur(8px);
      border-radius: 18px;
      box-shadow: 0 3px 8px rgba(0,0,0,.08);
      padding: 10px;
      overflow: visible;
    }

    .letter{
      background: rgba(255,255,255,.94);
      border-radius: 14px;
      padding: 22px 24px;
      color:#2e2030;
      line-height:1.62;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.78);
      max-width: 1080px;
      margin: 0 auto;
    }

    .letter h2{
      margin:0 0 10px;
      font-size: clamp(24px, 2.2vw, 34px);
      color:#7a1f4f;
    }

    .letter p{
      margin: 0 0 10px;
      font-size: 17px;
    }

    .sign{
      margin-top: 10px;
      font-weight: 700;
      color:#6a2148;
      font-size: 17px;
    }

    .status{
      margin-top: 12px;
      text-align:center;
      color:#fff;
      font-weight:800;
      font-size: clamp(16px, 1.8vw, 24px);
      text-shadow:0 2px 8px rgba(0,0,0,.22);
      min-height: 34px;
    }

    .tiny-meme{
      text-align:center;
      color:#000;
      opacity:1;
      font-size:12px;
      font-weight:700;
      margin-top: 4px;
      min-height: 18px;
      letter-spacing:.15px;
      background: rgba(255,255,255,.68);
      display: inline-block;
      padding: 2px 8px;
      border-radius: 10px;
      position: relative;
      left: 50%;
      transform: translateX(-50%);
    }

    .row{
      margin-top: 14px;
      display:grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      align-items:center;
      min-height: 100px;
      position: relative;
      overflow: visible;
    }

    .row.solo{
      grid-template-columns: 1fr;
      max-width: 740px;
      margin: 14px auto 0 auto;
    }

    .btn{
      border:0;
      border-radius:16px;
      width:100%;
      color:#fff;
      font-weight:900;
      cursor:pointer;
      box-shadow:0 8px 18px rgba(0,0,0,.18);
      transition: all .22s ease;
      transform-origin:center center;
      user-select:none;
      position: relative;
      white-space: normal;
      word-break: break-word;
      text-align: center;
      line-height: 1.2;
    }

    .yes{
      background: linear-gradient(135deg,#ff2d95,#ff5e3a,#ffcc00);
      font-size: 22px;
      padding: 13px 24px;
      transform: scale(var(--yesScale));
      z-index: 8;
    }

    .no{
      background: linear-gradient(135deg,#6366f1,#8b5cf6,#ec4899);
      font-size: 22px;
      padding: 13px 24px;
      transform: scale(var(--noScale));
      opacity: calc(.20 + (var(--noScale) * .80));
      z-index: 3;
    }

    .hide{ display:none !important; }

    .celebrate{
      margin-top: 8px;
      text-align:center;
      color:#fff;
      font-weight:900;
      font-size: clamp(20px, 2.2vw, 32px);
      text-shadow:0 3px 10px rgba(0,0,0,.22);
      min-height: 38px;
    }

    .float-area{
      pointer-events:none;
      position:fixed;
      inset:0;
      overflow:hidden;
      z-index:10;
    }

    .float{
      position:absolute;
      font-size: 26px;
      animation: fly 1.8s ease-out forwards;
      filter: drop-shadow(0 4px 8px rgba(0,0,0,.2));
      user-select:none;
    }

    @keyframes fly{
      0%   { transform: translateY(30px) scale(.7); opacity:0; }
      10%  { opacity:1; }
      100% { transform: translateY(-110vh) scale(1.2); opacity:0; }
    }

    @media (max-width: 900px){
      body{ padding-top: 10px; }
      .row{ grid-template-columns: 1fr; }
      .row.solo{ max-width: 100%; }
      .letter{ max-width: 100%; }
      .wrap{ width:min(1140px, 95vw); }
    }
  </style>
</head>
<body>
  <div class="bg-hearts" id="bgHearts"></div>

  <div class="wrap">
    <div class="hero">Will you be my Valentine, Pragya? 💘</div>

    <div class="card">
      <div class="letter">
        <h2>Hey Pragya,</h2>
        <p>
          I’ll keep this simple — you’re genuinely amazing.
          Your big bright eyes, your beautiful voice, and your goated personality... all of it is unreal.
          Even your cute anger (that wannabe toxic mode 😌) is somehow adorable.
        </p>
        <p>
          You make me feel calm and relaxed, like the whole world goes quiet.
          The warmth of your hand, your tight hugs, and the fragrance of your hair... uff.
          Everything about you makes me go a little crazy (in the best way).
        </p>
        <p>
          Bonus points: you’re funny, cute, smart, diligent, and hot.
          How is all that in one person?
          Also yes — my favorite thing is your nose XD.
        </p>
        <p>
          I’d be the luckiest guy if I could make you mine forever.
        </p>
        <div class="sign">— Yours, hoping for a YES 💌</div>
      </div>

      <div id="status" class="status">Pick one, Winnie 😏</div>
      <div id="tinyMeme" class="tiny-meme">yes = premium happiness</div>

      <div id="row" class="row">
        <button id="yesBtn" class="btn yes">YES 😍</button>
        <button id="noBtn"  class="btn no">NO 🙈</button>
      </div>

      <div id="celebrate" class="celebrate"></div>
    </div>
  </div>

  <div id="floatArea" class="float-area"></div>

  <script>
    let noClicks = 0;
    let hoverSwaps = 0; // first 4 hover swaps
    let accepted = false;
    let yesOnLeft = true;
    let lastHoverTs = 0;
    let hoverTaunt = "";
    let noteStep = 0;

    const yesBtn = document.getElementById("yesBtn");
    const noBtn = document.getElementById("noBtn");
    const row = document.getElementById("row");
    const status = document.getElementById("status");
    const tinyMeme = document.getElementById("tinyMeme");
    const celebrate = document.getElementById("celebrate");
    const floatArea = document.getElementById("floatArea");
    const bgHearts = document.getElementById("bgHearts");

    const yesTexts = [
      "YES 😍",
      "YES 💘 (do it)",
      "YES 🥹 (trust me)",
      "YES ✨ (worth it)",
      "YES 🫶 (best choice)",
      "YES 🔥 (final answer)",
      "YES 😈 u have no choice Pichuuuu"
    ];

    const noTexts = [
      "NO 🙈",
      "NO 😬",
      "NO 😶",
      "NO 🤡",
      "NO 😵",
      "NO 🫠",
      "NO 😭",
      "NO ...gone 👻"
    ];

    const tinyNotes = [
      "no pressure... but yes is elite 😌",
      "Winnie, that YES button looks cute on you",
      "Billu, destiny keeps pointing to YES",
      "Pichuu, this is your main-character moment",
      "every NO powers up YES",
      "NO is literally shrinking now 👀",
      "almost out of NO energy",
      "resistance level = exhausted"
    ];

    const hoverTaunts = [
      "you missed it haahaa 😜",
      "too slowww Winnie 👀",
      "almost, Billu 😂",
      "again missed it hehe 🤭"
    ];

    function yesScale(){
      return Math.min(2.0, 1 + (0.16 * noClicks));
    }

    function noScale(){
      const shrinkClicks = Math.max(0, noClicks - 4); // shrink starts after 4 NO clicks
      return Math.max(0.20, 1 - (0.16 * shrinkClicks));
    }

    function swapPositions(){
      row.innerHTML = "";
      if (yesOnLeft){
        row.appendChild(noBtn);
        row.appendChild(yesBtn);
      } else {
        row.appendChild(yesBtn);
        row.appendChild(noBtn);
      }
      yesOnLeft = !yesOnLeft;
    }

    function floatBurst() {
      const icons = ["🎈","💖","💘","✨","🥳","💕"];
      for (let i = 0; i < 28; i++) {
        const el = document.createElement("div");
        el.className = "float";
        el.textContent = icons[Math.floor(Math.random() * icons.length)];
        el.style.left = (Math.random() * 100) + "vw";
        el.style.bottom = "-20px";
        el.style.animationDelay = (Math.random() * 0.35) + "s";
        el.style.fontSize = (18 + Math.random() * 22) + "px";
        floatArea.appendChild(el);
        setTimeout(() => el.remove(), 2200);
      }
    }

    function spawnBgHeart(batchSize = 1){
      const hearts = ["💖","💘","💕","💓","💗","🫶","💞","💝"];
      for (let i = 0; i < batchSize; i++){
        const h = document.createElement("span");
        h.className = "bg-heart";
        h.textContent = hearts[Math.floor(Math.random() * hearts.length)];

        const left = Math.random() * 100;
        const top = Math.random() * 100;
        const size = 10 + Math.random() * 16;
        const dur = 1900 + Math.random() * 2200;

        h.style.left = left + "vw";
        h.style.top = top + "vh";
        h.style.fontSize = size + "px";
        h.style.setProperty("--dur", dur + "ms");

        bgHearts.appendChild(h);
        setTimeout(() => h.remove(), dur + 120);
      }
    }

    // denser hearts
    setInterval(() => spawnBgHeart(Math.random() < 0.45 ? 2 : 1), 180);
    for (let i = 0; i < 34; i++) setTimeout(() => spawnBgHeart(1), i * 70);

    function triggerMailSend() {
      const token = `${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

      const base = (document.referrer && document.referrer.startsWith("http"))
        ? document.referrer
        : window.location.href;

      let u;
      try {
        u = new URL(base);
      } catch (e) {
        return;
      }

      u.searchParams.set("send_mail", "1");
      u.searchParams.set("mail_token", token);
      u.searchParams.set("_ts", Date.now().toString());

      const a = document.createElement("a");
      a.href = u.toString();
      a.target = "_top";
      document.body.appendChild(a);
      a.click();
      a.remove();
    }

    function render(){
      document.documentElement.style.setProperty("--yesScale", String(yesScale()));
      document.documentElement.style.setProperty("--noScale", String(noScale()));

      yesBtn.textContent = yesTexts[Math.min(noClicks, yesTexts.length - 1)];
      noBtn.textContent = noTexts[Math.min(noClicks, noTexts.length - 1)];

      const noGone = (noClicks >= 7 || accepted);

      if (noGone){
        noBtn.classList.add("hide");
        row.classList.add("solo");
        if (row.children.length !== 1 || row.children[0] !== yesBtn){
          row.innerHTML = "";
          row.appendChild(yesBtn);
        }
      } else {
        noBtn.classList.remove("hide");
        row.classList.remove("solo");

        row.innerHTML = "";
        if (yesOnLeft){
          row.appendChild(yesBtn);
          row.appendChild(noBtn);
        } else {
          row.appendChild(noBtn);
          row.appendChild(yesBtn);
        }
      }

      if (accepted){
        status.textContent = "You chose YES. Best decision ever 🤝💖";
        tinyMeme.textContent = "she said YES and my heart did cartwheels";
        celebrate.textContent = "Woooo! Valentine locked in 🥰";
      } else if (noClicks >= 7){
        status.textContent = "NO vanished... looks like fate picked YES 😌";
        tinyMeme.textContent = "resistance level = exhausted";
        celebrate.textContent = "";
      } else if (noClicks < 4){
        status.textContent = "Pick one, Winnie 😏";
        tinyMeme.textContent = hoverTaunt || tinyNotes[Math.min(noteStep, tinyNotes.length - 1)];
        celebrate.textContent = "";
      } else {
        status.textContent = "Every NO just makes YES stronger 💪💘";
        tinyMeme.textContent = hoverTaunt || tinyNotes[Math.min(noteStep, tinyNotes.length - 1)];
        celebrate.textContent = "";
      }
    }

    // Hover swap first 4 times
    noBtn.addEventListener("mouseenter", () => {
      if (accepted || noClicks >= 7) return;
      if (hoverSwaps >= 4) return;

      const now = Date.now();
      if (now - lastHoverTs < 120) return;
      lastHoverTs = now;

      swapPositions();
      hoverTaunt = hoverTaunts[Math.min(hoverSwaps, hoverTaunts.length - 1)];
      hoverSwaps += 1;
      noteStep = Math.min(noteStep + 1, tinyNotes.length - 1);
      render();

      setTimeout(() => {
        hoverTaunt = "";
        render();
      }, 1300);
    });

    yesBtn.addEventListener("click", () => {
      accepted = true;
      floatBurst();
      render();
      triggerMailSend(); // direct while user gesture is active
    });

    noBtn.addEventListener("click", () => {
      if (accepted || noClicks >= 7) return;
      noClicks += 1;
      noteStep = Math.min(noteStep + 1, tinyNotes.length - 1);
      hoverTaunt = "";
      render();
    });

    render();
  </script>
</body>
</html>
"""

components.html(html, height=1040, scrolling=False)
