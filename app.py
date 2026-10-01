import streamlit as st
import sqlite3
import csv
import io
from datetime import datetime
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

APP_NAME = "Dead Phone Finder"
APP_VERSION = "2.0"

DB_PATH = Path("dead_phone_finder.db")


st.set_page_config(
    page_title=APP_NAME,
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROFESSIONAL CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top right, rgba(16,185,129,.12), transparent 30%),
        radial-gradient(circle at bottom left, rgba(59,130,246,.08), transparent 30%),
        #07111f;
    color: #f8fafc;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
}

.hero {
    padding: 30px;
    border-radius: 24px;
    background: linear-gradient(
        135deg,
        rgba(16,185,129,.18),
        rgba(15,23,42,.95)
    );
    border: 1px solid rgba(255,255,255,.08);
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 5px;
    font-weight: 800;
}

.hero p {
    color: #a7b4c7;
    font-size: 16px;
}

.card {
    padding: 22px;
    border-radius: 18px;
    background: rgba(15,23,42,.80);
    border: 1px solid rgba(255,255,255,.07);
    margin-bottom: 16px;
}

.stat {
    padding: 20px;
    border-radius: 18px;
    background: rgba(15,23,42,.9);
    border: 1px solid rgba(255,255,255,.07);
}

.stat-number {
    font-size: 30px;
    font-weight: 800;
}

.stat-label {
    color: #94a3b8;
    font-size: 13px;
}

.success-box {
    padding: 15px;
    border-radius: 14px;
    background: rgba(16,185,129,.10);
    border: 1px solid rgba(16,185,129,.3);
}

.warning-box {
    padding: 15px;
    border-radius: 14px;
    background: rgba(245,158,11,.10);
    border: 1px solid rgba(245,158,11,.3);
}

.info-box {
    padding: 15px;
    border-radius: 14px;
    background: rgba(59,130,246,.10);
    border: 1px solid rgba(59,130,246,.3);
}

.small {
    color: #94a3b8;
    font-size: 13px;
}

a {
    text-decoration: none !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS phones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            imei_last4 TEXT NOT NULL,
            model TEXT,
            color TEXT,
            last_location TEXT,
            status TEXT DEFAULT 'Registered',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            location TEXT,
            phone_model TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def add_phone(name, imei, model, color, location):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()

    conn.execute("""
        INSERT INTO phones
        (name, imei_last4, model, color, last_location,
         status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        imei[-4:],
        model,
        color,
        location,
        "Registered",
        now,
        now
    ))

    conn.commit()
    conn.close()


def get_phones():

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            id,
            name,
            imei_last4,
            model,
            color,
            last_location,
            status,
            created_at
        FROM phones
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return rows


def update_phone_status(phone_id, status):

    conn = get_connection()

    conn.execute("""
        UPDATE phones
        SET status = ?, updated_at = ?
        WHERE id = ?
    """, (
        status,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        phone_id
    ))

    conn.commit()
    conn.close()


def delete_phone(phone_id):

    conn = get_connection()

    conn.execute(
        "DELETE FROM phones WHERE id = ?",
        (phone_id,)
    )

    conn.commit()
    conn.close()


def add_alert(message, location, model):

    conn = get_connection()

    conn.execute("""
        INSERT INTO alerts
        (message, location, phone_model, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        message,
        location,
        model,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_alerts():

    conn = get_connection()

    rows = conn.execute("""
        SELECT message, location, phone_model, created_at
        FROM alerts
        ORDER BY id DESC
        LIMIT 50
    """).fetchall()

    conn.close()

    return rows


# ============================================================
# AI HELP ENGINE
# ============================================================

def ai_help(question):

    q = question.lower().strip()

    if not q:
        return "Please describe what happened to your phone."

    if any(x in q for x in [
        "dead",
        "battery",
        "switched off",
        "power off",
        "no battery"
    ]):

        return """
### 🔋 If your phone is powered off

1. Open Google Find My Device or Apple Find My.
2. Check the **last known location**.
3. Check when the device was last seen.
4. If someone may have found it, do not confront them.
5. If the phone is stolen, contact the police and use the official CEIR process for IMEI blocking in India.

A dead phone cannot normally transmit a new GPS location by itself.
"""

    if "imei" in q:

        return """
### 🔐 IMEI protection

Your IMEI is a sensitive device identifier.

For India:

- Keep the original IMEI/documentation safely.
- Use the official CEIR service for blocking/recovering eligibility.
- Do not publish the complete IMEI publicly.
- Do not share OTPs with people claiming they found your phone.
"""

    if any(x in q for x in ["stolen", "steal", "robbed"]):

        return """
### 🚨 If your phone was stolen

**Do this in order:**

1. Try Google Find My Device / Apple Find My.
2. Lock the phone remotely if available.
3. Do not meet a suspected thief yourself.
4. Contact police if theft is involved.
5. Keep your IMEI and purchase proof ready.
6. Consider blocking the device through India's CEIR system.
7. Change important passwords if the device was unlocked.
"""

    if any(x in q for x in ["lost", "missing"]):

        return """
### 🔎 If your phone is missing

Start with:

**Last location → Remote lock → Call → Community alert → Police/CEIR if necessary**

Also check:
- Vehicle
- College/classroom
- Home
- Shops visited recently
- Friends/family
- Transport used
"""

    if any(x in q for x in ["google", "android"]):

        return """
### 🤖 Android

Use Google's official Find My Device service.

You may be able to:
- See last known location
- Play sound
- Secure the device
- Display contact information
- Erase the device when appropriate
"""

    if any(x in q for x in ["iphone", "apple", "ios"]):

        return """
### 🍎 iPhone

Use Apple's Find My service.

Check:
- Last known location
- Lost Mode
- Contact information
- Device status

Avoid sharing your Apple ID password or verification codes.
"""

    if "police" in q or "fir" in q:

        return """
### 👮 Police report

If the phone was stolen or there is suspected criminal activity:

- Preserve purchase information.
- Keep the IMEI available.
- Record the approximate time/place.
- Contact the appropriate police authority.
- Use India's official cybercrime reporting service where applicable.
"""

    return """
### 🤖 Recovery checklist

I recommend this sequence:

**1. Last known location**

**2. Google Find My Device / Apple Find My**

**3. Lock the device**

**4. Call the phone**

**5. Ask nearby people/security**

**6. Broadcast a community alert**

**7. Police / CEIR when appropriate**

Never share OTPs, passwords or full banking credentials with someone claiming they found your phone.
"""


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">

<h1>📱 Dead Phone Finder</h1>

<p>
A practical recovery assistant for lost, missing or powered-off phones.
</p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📱 Dead Phone Finder")

    st.caption("Professional Recovery Assistant")

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📱 My Phones",
            "📢 Community Alerts",
            "🤖 Recovery Assistant",
            "🛡️ Safety Toolkit"
        ]
    )

    st.divider()

    st.caption(f"Version {APP_VERSION}")

    st.info(
        "This app does not secretly track phones. "
        "It organizes recovery information and connects users "
        "to official services."
    )


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    phones = get_phones()
    alerts = get_alerts()

    total = len(phones)

    lost = sum(
        1 for p in phones
        if p[6] == "Lost"
    )

    found = sum(
        1 for p in phones
        if p[6] == "Found"
    )

    active_alerts = len(alerts)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-number">{total}</div>
                <div class="stat-label">REGISTERED PHONES</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-number">{lost}</div>
                <div class="stat-label">MARKED LOST</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-number">{found}</div>
                <div class="stat-label">FOUND</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-number">{active_alerts}</div>
                <div class="stat-label">COMMUNITY ALERTS</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    st.markdown(
        """
        <div class="info-box">

        <b>🚀 Recommended recovery sequence</b>

        <br><br>

        Last known location → Find My Device → Lock phone →
        Call → Community alert → Police/CEIR if necessary

        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("⚡ Quick Actions")

    a, b, c = st.columns(3)

    with a:
        if st.button(
            "📱 Register Phone",
            use_container_width=True
        ):
            st.info("Open **My Phones** from the sidebar.")

    with b:
        if st.button(
            "📢 Create Alert",
            use_container_width=True
        ):
            st.info("Open **Community Alerts**.")

    with c:
        if st.button(
            "🤖 Ask Recovery Assistant",
            use_container_width=True
        ):
            st.info("Open **Recovery Assistant**.")


# ============================================================
# MY PHONES
# ============================================================

elif page == "📱 My Phones":

    st.header("📱 My Phones")

    st.caption(
        "Register devices so you can quickly access their recovery information."
    )

    with st.expander(
        "➕ Register a new phone",
        expanded=True
    ):

        with st.form("phone_registration"):

            c1, c2 = st.columns(2)

            with c1:

                name = st.text_input(
                    "Device nickname *",
                    placeholder="My Redmi"
                )

                model = st.text_input(
                    "Phone model",
                    placeholder="Redmi Note 14"
                )

                color = st.text_input(
                    "Colour",
                    placeholder="Black"
                )

            with c2:

                imei = st.text_input(
                    "IMEI *",
                    placeholder="Enter 15-digit IMEI",
                    type="password"
                )

                location = st.text_input(
                    "Last known location",
                    placeholder="College campus, Hassan"
                )

            submit = st.form_submit_button(
                "🔐 Securely Register Phone",
                use_container_width=True
            )

            if submit:

                if not name.strip():
                    st.error("Enter a device nickname.")

                elif not imei.isdigit() or len(imei) != 15:
                    st.error(
                        "IMEI should contain exactly 15 digits."
                    )

                else:

                    add_phone(
                        name.strip(),
                        imei,
                        model.strip(),
                        color.strip(),
                        location.strip()
                    )

                    st.success(
                        f"✅ {name} registered successfully."
                    )

                    st.rerun()

    st.divider()

    phones = get_phones()

    search = st.text_input(
        "🔎 Search your devices",
        placeholder="Search by name, model or location"
    )

    for p in phones:

        phone_id = p[0]
        name = p[1]
        imei_last4 = p[2]
        model = p[3]
        color = p[4]
        location = p[5]
        status = p[6]
        created = p[7]

        searchable = (
            f"{name} {model} {color} {location}"
        ).lower()

        if search and search.lower() not in searchable:
            continue

        with st.container(border=True):

            c1, c2 = st.columns([3, 1])

            with c1:

                st.subheader(
                    f"📱 {name}"
                )

                st.write(
                    f"**Model:** {model or 'Not specified'}"
                )

                st.write(
                    f"**Colour:** {color or 'Not specified'}"
                )

                st.write(
                    f"**IMEI:** ****{imei_last4}"
                )

                st.write(
                    f"**Last known location:** "
                    f"{location or 'Not specified'}"
                )

                st.caption(
                    f"Registered: {created}"
                )

            with c2:

                st.write(
                    f"### {status}"
                )

                new_status = st.selectbox(
                    "Status",
                    [
                        "Registered",
                        "Lost",
                        "Found"
                    ],
                    index=[
                        "Registered",
                        "Lost",
                        "Found"
                    ].index(status),
                    key=f"status_{phone_id}"
                )

                if st.button(
                    "Update",
                    key=f"update_{phone_id}",
                    use_container_width=True
                ):

                    update_phone_status(
                        phone_id,
                        new_status
                    )

                    st.success("Updated")
                    st.rerun()

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{phone_id}",
                    use_container_width=True
                ):

                    delete_phone(phone_id)

                    st.warning("Device deleted.")
                    st.rerun()


# ============================================================
# COMMUNITY ALERTS
# ============================================================

elif page == "📢 Community Alerts":

    st.header("📢 Community Alert Network")

    st.markdown(
        """
        <div class="warning-box">

        ⚠️ Do not publish sensitive information such as:
        full IMEI, OTP, passwords, banking information or home address.

        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("alert_form"):

        message = st.text_area(
            "What happened?",
            placeholder=(
                "Lost black Redmi near Hassan bus stand. "
                "Please contact me if found."
            )
        )

        c1, c2 = st.columns(2)

        with c1:

            location = st.text_input(
                "Approximate area",
                placeholder="Hassan bus stand"
            )

        with c2:

            model = st.text_input(
                "Phone model",
                placeholder="Redmi Note"
            )

        submit_alert = st.form_submit_button(
            "📢 Broadcast Alert",
            use_container_width=True
        )

        if submit_alert:

            if len(message.strip()) < 10:
                st.error(
                    "Please provide a little more information."
                )

            else:

                add_alert(
                    message.strip(),
                    location.strip(),
                    model.strip()
                )

                st.success(
                    "📢 Community alert created."
                )

                st.rerun()

    st.divider()

    st.subheader("🌐 Recent Community Alerts")

    alerts = get_alerts()

    if not alerts:

        st.info(
            "No community alerts yet."
        )

    for message, location, model, created in alerts:

        with st.container(border=True):

            st.markdown(
                f"### 📱 {model or 'Lost phone'}"
            )

            st.write(message)

            if location:
                st.caption(
                    f"📍 Approximate area: {location}"
                )

            st.caption(
                f"🕒 {created}"
            )


# ============================================================
# AI ASSISTANT
# ============================================================

elif page == "🤖 Recovery Assistant":

    st.header("🤖 Recovery Assistant")

    st.caption(
        "Describe what happened and get a structured recovery checklist."
    )

    question = st.text_area(
        "What happened to your phone?",
        placeholder=(
            "Example: My Redmi battery died and I lost it "
            "near my college. What should I do?"
        ),
        height=130
    )

    if st.button(
        "🤖 Generate Recovery Plan",
        use_container_width=True
    ):

        if question.strip():

            answer = ai_help(question)

            st.markdown(
                f"""
                <div class="card">
                {answer}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.warning(
                "Describe your situation first."
            )

    st.divider()

    st.subheader("💡 Common Questions")

    questions = [
        "My phone battery is dead",
        "My phone was stolen",
        "I lost my Android phone",
        "How can I protect my IMEI?",
        "I lost my iPhone",
        "How do I report phone theft?"
    ]

    for question_text in questions:

        if st.button(
            question_text,
            use_container_width=True
        ):

            st.markdown(
                ai_help(question_text)
            )


# ============================================================
# SAFETY TOOLKIT
# ============================================================

elif page == "🛡️ Safety Toolkit":

    st.header("🛡️ Official Recovery Toolkit")

    st.markdown(
        """
        Use official services whenever possible.
        Avoid unofficial websites asking for passwords,
        OTPs or payment to locate your phone.
        """
    )

    resources = [
        (
            "🤖 Google Find My Device",
            "https://www.google.com/android/find",
            "For Android devices."
        ),
        (
            "🍎 Apple Find My",
            "https://www.icloud.com/find",
            "For iPhone and Apple devices."
        ),
        (
            "🇮🇳 CEIR",
            "https://www.ceir.gov.in",
            "India's official IMEI-related device blocking system."
        ),
        (
            "👮 National Cyber Crime Portal",
            "https://cybercrime.gov.in",
            "For eligible cybercrime reporting."
        ),
        (
            "🗺️ Google Timeline",
            "https://timeline.google.com",
            "Check your own location history when available."
        )
    ]

    for title, url, description in resources:

        st.markdown(
            f"""
            <div class="card">

            <h3>{title}</h3>

            <p>{description}</p>

            <a href="{url}" target="_blank">
            🔗 Open Official Service
            </a>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    st.subheader("🚨 Important Safety Rules")

    rules = [
        "Never share OTPs with strangers.",
        "Never share your Google/Apple password.",
        "Do not publish your full IMEI publicly.",
        "Do not meet a suspected thief alone.",
        "Do not pay strangers claiming they can unlock or locate your phone.",
        "Use official government/company websites whenever possible."
    ]

    for rule in rules:
        st.write(f"• {rule}")


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "📱 Dead Phone Finder • Built as a CSE portfolio project • "
    "Recovery assistance, not a guaranteed device-tracking service."
)
