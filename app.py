import streamlit as st
st.set_page_config(page_title="Dead Phone Finder", page_icon="📱", layout="wide")
st.markdown("<style>h1{color:#10b981;}</style>", unsafe_allow_html=True)
st.title("📱 Dead Phone Finder")
st.subheader("Find it even when it's dead — for the common man")

if "phones" not in st.session_state:
    st.session_state.phones = []
if "alerts" not in st.session_state:
    st.session_state.alerts = ["Spotted black Redmi near MG Road, Bengaluru - 10 min ago"]

KB = {
 "dead":"If battery dead: Check last-known location in Google Timeline, call it, use crowd alert below.",
 "battery":"Enable battery saver, check Google Find My Device last location.",
 "fir":"File FIR at cybercrime.gov.in and block IMEI at ceir.gov.in",
 "imei":"Block IMEI at ceir.gov.in to prevent misuse.",
 "find my":"Use google.com/android/find or iCloud.com/find",
}

def ai(q):
    ql=q.lower()
    for k,v in KB.items():
        if k in ql: return v
    return "Try: last location → crowd alert → block IMEI → file FIR. Ask about 'dead', 'imei', 'fir'."

tab1,tab2,tab3,tab4 = st.tabs(["📝 Register Phone","🤖 AI Help","📢 Crowd Alert","🔗 Safety Toolkit"])

with tab1:
    st.header("Register your phone")
    with st.form("reg"):
        name=st.text_input("Phone name", "My Redmi Note")
        imei=st.text_input("IMEI last 4 digits", "1234")
        color=st.text_input("Color/Model", "Black Redmi")
        last_loc=st.text_input("Last seen location", "MG Road, Bengaluru")
        s=st.form_submit_button("Register")
        if s:
            st.session_state.phones.insert(0, {"name":name,"imei":imei,"color":color,"loc":last_loc})
            st.success(f"Registered {name}! Now broadcast a crowd alert.")
    for p in st.session_state.phones:
        st.info(f"📱 {p['name']} | {p['color']} | IMEI ****{p['imei']} | Last: {p['loc']}")

with tab2:
    st.header("AI Help")
    q=st.text_input("Ask", placeholder="My battery is dead, what to do?")
    if st.button("Ask AI"):
        st.success("🤖 "+ai(q))

with tab3:
    st.header("Broadcast Crowd Alert")
    msg=st.text_input("Alert message", placeholder="Lost black Redmi near MG Road")
    if st.button("Broadcast"):
        if msg: st.session_state.alerts.insert(0, msg+" - just now"); st.success("Alert broadcasted!")
    st.header("Live Community Feed")
    for a in st.session_state.alerts: st.write("• "+a)

with tab4:
    st.header("Direct Safety Links")
    st.markdown("""
- [Google Find My Device](https://www.google.com/android/find)
- [Apple Find My](https://www.icloud.com/find)
- [CEIR - Block IMEI (India)](https://www.ceir.gov.in)
- [Cybercrime FIR Portal](https://cybercrime.gov.in)
- [Google Timeline - Last Location](https://timeline.google.com)
""")
    st.header("What to do - 4 Steps")
    st.write("1. Check last known location 2. Call / Play sound 3. Broadcast crowd alert 4. Block IMEI + File FIR")

st.sidebar.info("Project 2 by Bharath Gowda | 2nd year CSE")
