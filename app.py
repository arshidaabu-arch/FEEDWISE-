import streamlit as st
import sqlite3, hashlib, hmac, secrets, re
from datetime import datetime
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
import pandas as pd

DB=Path(__file__).parent/"feedwise.db"
st.set_page_config(page_title="FEEDWISE Farmer Portal",page_icon="🌾",layout="wide")

LANGS = {
    "English":"en", "தமிழ் (Tamil)":"ta", "മലയാളം (Malayalam)":"ml",
    "ಕನ್ನಡ (Kannada)":"kn", "తెలుగు (Telugu)":"te", "हिन्दी (Hindi)":"hi",
    "বাংলা (Bengali)":"bn", "मराठी (Marathi)":"mr", "ગુજરાતી (Gujarati)":"gu",
    "ਪੰਜਾਬੀ (Punjabi)":"pa", "ଓଡ଼ିଆ (Odia)":"or", "অসমীয়া (Assamese)":"as",
    "اردو (Urdu)":"ur", "संस्कृतम् (Sanskrit)":"sa", "कोंकणी (Konkani)":"kok",
    "মৈথিলী (Maithili)":"mai", "डोगरी (Dogri)":"doi", "کٲشُر (Kashmiri)":"ks",
    "संताली (Santali)":"sat", "سنڌي (Sindhi)":"sd", "बड़ो (Bodo)":"brx",
    "মৈতেই (Manipuri)":"mni"
}
# Starter translations for the most-used labels; other text falls back to English.
WORDS = {
"ta":{tr("Sign in"):"உள்நுழைக",tr("Create account"):"கணக்கை உருவாக்கு",tr("Welcome back"):"மீண்டும் வரவேற்கிறோம்",tr("Farmer registration"):"விவசாயி பதிவு",tr("Farmer name"):"விவசாயியின் பெயர்",tr("Mobile number"):"கைபேசி எண்",tr("Password"):"கடவுச்சொல்",tr("Create password"):"கடவுச்சொல்லை உருவாக்கு",tr("Confirm password"):"கடவுச்சொல்லை உறுதிப்படுத்து",tr("Navigation"):"மெனு",tr("Home"):"முகப்பு",tr("New Test"):"புதிய சோதனை",tr("Test History"):"சோதனை வரலாறு",tr("Nutritional Guide"):"ஊட்டச்சத்து வழிகாட்டி",tr("Feed Recommendation"):"தீவனப் பரிந்துரை",tr("Sign out"):"வெளியேறு",tr("Feed type"):"தீவன வகை",tr("Cattle feed"):"கால்நடைத் தீவனம்",tr("Silage"):"புளிக்கவைத்த பசுந்தீவனம்",tr("Hay / fodder"):"உலர் புல் / தீவனம்",tr("Other"):"மற்றவை",tr("Image source"):"படம் எடுக்கும் முறை",tr("Camera"):"கேமரா",tr("Upload"):"பதிவேற்றம்",tr("Measured moisture (%)"):"அளந்த ஈரப்பதம் (%)",tr("Measured crude protein (%)"):"அளந்த கச்சா புரதம் (%)",tr("Target crude protein (%)"):"தேவையான கச்சா புரதம் (%)",tr("Notes (optional)"):"குறிப்புகள் (விருப்பம்)",tr("Analyse and save test"):"பகுப்பாய்வு செய்து சேமிக்கவும்",tr("My Test History"):"எனது சோதனை வரலாறு",tr("Download my history as CSV"):"எனது வரலாற்றை CSV ஆகப் பதிவிறக்கவும்",tr("Saved tests"):"சேமித்த சோதனைகள்",tr("Average moisture"):"சராசரி ஈரப்பதம்",tr("Average protein"):"சராசரி புரதம்"},
"ml":{tr("Sign in"):"സൈൻ ഇൻ",tr("Create account"):"അക്കൗണ്ട് സൃഷ്ടിക്കുക",tr("Welcome back"):"വീണ്ടും സ്വാഗതം",tr("Farmer registration"):"കർഷക രജിസ്ട്രേഷൻ",tr("Farmer name"):"കർഷകന്റെ പേര്",tr("Mobile number"):"മൊബൈൽ നമ്പർ",tr("Password"):"പാസ്‌വേഡ്",tr("Create password"):"പാസ്‌വേഡ് സൃഷ്ടിക്കുക",tr("Confirm password"):"പാസ്‌വേഡ് സ്ഥിരീകരിക്കുക",tr("Navigation"):"നാവിഗേഷൻ",tr("Home"):"ഹോം",tr("New Test"):"പുതിയ പരിശോധന",tr("Test History"):"പരിശോധനാ ചരിത്രം",tr("Nutritional Guide"):"പോഷകാഹാര മാർഗ്ഗദർശി",tr("Feed Recommendation"):"തീറ്റ നിർദേശം",tr("Sign out"):"സൈൻ ഔട്ട്",tr("Feed type"):"തീറ്റയുടെ തരം",tr("Cattle feed"):"കന്നുകാലി തീറ്റ",tr("Silage"):"സൈലേജ്",tr("Hay / fodder"):"ഉണങ്ങിയ പുല്ല് / തീറ്റ",tr("Other"):"മറ്റുള്ളവ",tr("Image source"):"ചിത്രത്തിന്റെ ഉറവിടം",tr("Camera"):"ക്യാമറ",tr("Upload"):"അപ്‌ലോഡ്",tr("Measured moisture (%)"):"അളന്ന ഈർപ്പം (%)",tr("Measured crude protein (%)"):"അളന്ന ക്രൂഡ് പ്രോട്ടീൻ (%)",tr("Target crude protein (%)"):"ലക്ഷ്യ ക്രൂഡ് പ്രോട്ടീൻ (%)",tr("Notes (optional)"):"കുറിപ്പുകൾ (ഐച്ഛികം)",tr("Analyse and save test"):"വിശകലനം ചെയ്ത് സൂക്ഷിക്കുക",tr("My Test History"):"എന്റെ പരിശോധനാ ചരിത്രം",tr("Download my history as CSV"):"എന്റെ ചരിത്രം CSV ആയി ഡൗൺലോഡ് ചെയ്യുക",tr("Saved tests"):"സേവ് ചെയ്ത പരിശോധനകൾ",tr("Average moisture"):"ശരാശരി ഈർപ്പം",tr("Average protein"):"ശരാശരി പ്രോട്ടീൻ"},
"hi":{tr("Sign in"):"लॉग इन करें",tr("Create account"):"खाता बनाएँ",tr("Welcome back"):"वापसी पर स्वागत है",tr("Farmer registration"):"किसान पंजीकरण",tr("Farmer name"):"किसान का नाम",tr("Mobile number"):"मोबाइल नंबर",tr("Password"):"पासवर्ड",tr("Create password"):"पासवर्ड बनाएँ",tr("Confirm password"):"पासवर्ड की पुष्टि करें",tr("Navigation"):"नेविगेशन",tr("Home"):"होम",tr("New Test"):"नई जाँच",tr("Test History"):"जाँच इतिहास",tr("Nutritional Guide"):"पोषण मार्गदर्शिका",tr("Feed Recommendation"):"चारा सुझाव",tr("Sign out"):"लॉग आउट",tr("Feed type"):"चारे का प्रकार",tr("Cattle feed"):"पशु आहार",tr("Silage"):"साइलेज",tr("Hay / fodder"):"सूखा चारा",tr("Other"):"अन्य",tr("Image source"):"चित्र का स्रोत",tr("Camera"):"कैमरा",tr("Upload"):"अपलोड",tr("Measured moisture (%)"):"मापी गई नमी (%)",tr("Measured crude protein (%)"):"मापा गया क्रूड प्रोटीन (%)",tr("Target crude protein (%)"):"लक्षित क्रूड प्रोटीन (%)",tr("Notes (optional)"):"टिप्पणियाँ (वैकल्पिक)",tr("Analyse and save test"):"विश्लेषण करें और सहेजें",tr("My Test History"):"मेरी जाँच का इतिहास",tr("Download my history as CSV"):"इतिहास CSV में डाउनलोड करें",tr("Saved tests"):"सहेजी गई जाँच",tr("Average moisture"):"औसत नमी",tr("Average protein"):"औसत प्रोटीन"},
"te":{tr("Sign in"):"సైన్ ఇన్",tr("Create account"):"ఖాతా సృష్టించండి",tr("Welcome back"):"మళ్లీ స్వాగతం",tr("Farmer registration"):"రైతు నమోదు",tr("Farmer name"):"రైతు పేరు",tr("Mobile number"):"మొబైల్ నంబర్",tr("Password"):"పాస్‌వర్డ్",tr("Create password"):"పాస్‌వర్డ్ సృష్టించండి",tr("Confirm password"):"పాస్‌వర్డ్ నిర్ధారించండి",tr("Navigation"):"నావిగేషన్",tr("Home"):"హోమ్",tr("New Test"):"కొత్త పరీక్ష",tr("Test History"):"పరీక్షల చరిత్ర",tr("Nutritional Guide"):"పోషకాహార మార్గదర్శి",tr("Feed Recommendation"):"మేత సూచన",tr("Sign out"):"సైన్ అవుట్",tr("Feed type"):"మేత రకం",tr("Cattle feed"):"పశువుల మేత",tr("Silage"):"సైలేజ్",tr("Hay / fodder"):"ఎండిన గడ్డి / మేత",tr("Other"):"ఇతర",tr("Image source"):"చిత్ర మూలం",tr("Camera"):"కెమెరా",tr("Upload"):"అప్‌లోడ్",tr("Measured moisture (%)"):"కొలిచిన తేమ (%)",tr("Measured crude protein (%)"):"కొలిచిన క్రూడ్ ప్రోటీన్ (%)",tr("Target crude protein (%)"):"లక్ష్య క్రూడ్ ప్రోటీన్ (%)",tr("Notes (optional)"):"గమనికలు (ఐచ్ఛికం)",tr("Analyse and save test"):"విశ్లేషించి సేవ్ చేయండి",tr("My Test History"):"నా పరీక్షల చరిత్ర",tr("Download my history as CSV"):"చరిత్రను CSVగా డౌన్‌లోడ్ చేయండి",tr("Saved tests"):"సేవ్ చేసిన పరీక్షలు",tr("Average moisture"):"సగటు తేమ",tr("Average protein"):"సగటు ప్రోటీన్"},
"kn":{tr("Sign in"):"ಲಾಗಿನ್",tr("Create account"):"ಖಾತೆ ರಚಿಸಿ",tr("Welcome back"):"ಮತ್ತೆ ಸ್ವಾಗತ",tr("Farmer registration"):"ರೈತರ ನೋಂದಣಿ",tr("Farmer name"):"ರೈತರ ಹೆಸರು",tr("Mobile number"):"ಮೊಬೈಲ್ ಸಂಖ್ಯೆ",tr("Password"):"ಪಾಸ್‌ವರ್ಡ್",tr("Create password"):"ಪಾಸ್‌ವರ್ಡ್ ರಚಿಸಿ",tr("Confirm password"):"ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ",tr("Navigation"):"ನ್ಯಾವಿಗೇಶನ್",tr("Home"):"ಮುಖಪುಟ",tr("New Test"):"ಹೊಸ ಪರೀಕ್ಷೆ",tr("Test History"):"ಪರೀಕ್ಷಾ ಇತಿಹಾಸ",tr("Nutritional Guide"):"ಪೌಷ್ಟಿಕ ಮಾರ್ಗದರ್ಶಿ",tr("Feed Recommendation"):"ಮೇವಿನ ಸಲಹೆ",tr("Sign out"):"ಲಾಗ್ ಔಟ್",tr("Feed type"):"ಮೇವಿನ ವಿಧ",tr("Cattle feed"):"ಜಾನುವಾರು ಮೇವು",tr("Silage"):"ಸೈಲೇಜ್",tr("Hay / fodder"):"ಒಣ ಹುಲ್ಲು / ಮೇವು",tr("Other"):"ಇತರೆ",tr("Image source"):"ಚಿತ್ರದ ಮೂಲ",tr("Camera"):"ಕ್ಯಾಮೆರಾ",tr("Upload"):"ಅಪ್‌ಲೋಡ್",tr("Measured moisture (%)"):"ಅಳತೆ ಮಾಡಿದ ತೇವಾಂಶ (%)",tr("Measured crude protein (%)"):"ಅಳತೆ ಮಾಡಿದ ಕಚ್ಚಾ ಪ್ರೋಟೀನ್ (%)",tr("Target crude protein (%)"):"ಗುರಿ ಕಚ್ಚಾ ಪ್ರೋಟೀನ್ (%)",tr("Notes (optional)"):"ಟಿಪ್ಪಣಿಗಳು (ಐಚ್ಛಿಕ)",tr("Analyse and save test"):"ವಿಶ್ಲೇಷಿಸಿ ಉಳಿಸಿ",tr("My Test History"):"ನನ್ನ ಪರೀಕ್ಷಾ ಇತಿಹಾಸ",tr("Download my history as CSV"):"ಇತಿಹಾಸವನ್ನು CSV ಆಗಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ",tr("Saved tests"):"ಉಳಿಸಿದ ಪರೀಕ್ಷೆಗಳು",tr("Average moisture"):"ಸರಾಸರಿ ತೇವಾಂಶ",tr("Average protein"):"ಸರಾಸರಿ ಪ್ರೋಟೀನ್"}
}
def tr(label):
    code=st.session_state.get("feedwise_language","en")
    return WORDS.get(code,{}).get(label,label)


def conn():
    c=sqlite3.connect(DB,check_same_thread=False); c.row_factory=sqlite3.Row; return c
def init():
    with conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS farmers(id INTEGER PRIMARY KEY,name TEXT NOT NULL,phone TEXT UNIQUE NOT NULL,salt BLOB NOT NULL,pwh BLOB NOT NULL)")
        c.execute("""CREATE TABLE IF NOT EXISTS tests(id INTEGER PRIMARY KEY,farmer_id INTEGER,date TEXT,feed TEXT,moisture REAL,protein REAL,target REAL,score REAL,notes TEXT,FOREIGN KEY(farmer_id) REFERENCES farmers(id))""")
def phash(p,s): return hashlib.pbkdf2_hmac("sha256",p.encode(),s,240000)
def register(name,phone,pw):
    salt=secrets.token_bytes(16)
    try:
        with conn() as c:c.execute("INSERT INTO farmers(name,phone,salt,pwh) VALUES(?,?,?,?)",(name.strip(),phone.strip(),salt,phash(pw,salt)))
        return True,"Account created. Please sign in."
    except sqlite3.IntegrityError:return False,"That phone number is already registered."
def login(phone,pw):
    with conn() as c:r=c.execute("SELECT * FROM farmers WHERE phone=?",(phone.strip(),)).fetchone()
    return dict(r) if r and hmac.compare_digest(phash(pw,r["salt"]),r["pwh"]) else None
def tests(uid):
    with conn() as c:return c.execute("SELECT * FROM tests WHERE farmer_id=? ORDER BY id DESC",(uid,)).fetchall()
def visual(img):
    a=np.array(img.convert("RGB")); h,w=a.shape[:2]; s=min(1,700/max(h,w))
    if s<1:a=cv2.resize(a,(int(w*s),int(h*s)))
    hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV); gray=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
    dark=(gray<55).mean(); pale=((hsv[:,:,2]>165)&(hsv[:,:,1]<45)).mean()
    green=((hsv[:,:,0]>=25)&(hsv[:,:,0]<=95)&(hsv[:,:,1]>45)&(hsv[:,:,2]>35)).mean()
    texture=cv2.Laplacian(gray,cv2.CV_64F).var()
    return min(100,100*(.4*min(dark/.2,1)+.3*min(pale/.35,1)+.2*min(green/.2,1)+.1*min(texture/1200,1)))
def save(uid,feed,m,p,t,s,n):
    with conn() as c:c.execute("INSERT INTO tests(farmer_id,date,feed,moisture,protein,target,score,notes) VALUES(?,?,?,?,?,?,?,?)",(uid,datetime.now().isoformat(timespec="minutes"),feed,m,p,t,s,n))

st.markdown("""<style>
.block-container{padding-top:1.2rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#087a4b,#064b35)}
[data-testid="stSidebar"] *{color:white!important}
.hero{background:linear-gradient(110deg,#e8f5ed,#f7fbf8);border:1px solid #cfe7d8;padding:18px 22px;border-radius:15px;margin-bottom:14px}
.hero h1{color:#075638;margin:0}.hero p{color:#334155;margin:5px 0 0}
div.stButton>button[kind="primary"]{background:#087a4b;border-color:#087a4b}
</style>""",unsafe_allow_html=True)
init()
if "feedwise_language" not in st.session_state:
    st.session_state.feedwise_language = "en"
chosen_language = st.selectbox("🌐 Language / மொழி", list(LANGS.keys()),
    index=list(LANGS.values()).index(st.session_state.feedwise_language),
    key="feedwise_language_picker")
st.session_state.feedwise_language = LANGS[chosen_language]

if "user" not in st.session_state:
    st.markdown('<div class="hero"><h1>🌾 FEEDWISE Farmer Portal</h1><p>Camera-assisted feed screening and individual farm records</p></div>',unsafe_allow_html=True)
    a,b=st.columns([1,1],gap="large")
    with a:
        st.image("https://images.unsplash.com/photo-1500595046743-cd271d694d30?w=900",use_container_width=True)
        st.subheader("Your farm. Your records.")
        st.write("Create your own account to keep your feed test history separate.")
    with b:
        t1,t2=st.tabs(["🔐 Sign in","🌱 Create account"])
        with t1:
            st.subheader(tr("Welcome back"))
            with st.form("login"):
                phone=st.text_input(tr("Mobile number")); pw=st.text_input(tr("Password"),type="password")
                ok=st.form_submit_button(tr("Sign in"),type="primary",use_container_width=True)
            if ok:
                u=login(phone,pw)
                if u:st.session_state.user=u; st.rerun()
                else:st.error("Incorrect phone number or password.")
        with t2:
            st.subheader(tr("Farmer registration"))
            with st.form("register"):
                name=st.text_input(tr("Farmer name")); phone=st.text_input(tr("Mobile number"),key="newphone")
                pw=st.text_input(tr("Create password"),type="password",key="newpw")
                cp=st.text_input(tr("Confirm password"),type="password")
                ok=st.form_submit_button(tr("Create account"),type="primary",use_container_width=True)
            if ok:
                if not name.strip() or not phone.strip() or not pw:st.error("Complete all fields.")
                elif not re.fullmatch(r"[0-9+ -]{8,16}",phone.strip()):st.error("Enter a valid phone number.")
                elif len(pw)<8:st.error("Password must contain at least 8 characters.")
                elif pw!=cp:st.error("Passwords do not match.")
                else:
                    success,msg=register(name,phone,pw); (st.success if success else st.error)(msg)
    st.caption("Demonstration login only. Public deployment requires persistent database storage and a security review.")
    st.stop()

u=st.session_state.user
with st.sidebar:
    st.markdown("## 🐄 FEEDWISE")
    st.write("Farmer: **"+u["name"]+"**"); st.caption(u["phone"])
    page=st.radio(tr("Navigation"),[tr("Home"),tr("New Test"),tr("Test History"),tr("Nutritional Guide"),tr("Feed Recommendation")])
    if st.button(tr("Sign out"),use_container_width=True):st.session_state.pop("user"); st.rerun()
    st.markdown("---"); st.caption("SIH prototype")

if page==tr("Home"):
    st.markdown(f'<div class="hero"><h1>Welcome, {u["name"]} 👋</h1><p>Review your feed records or start a new screening.</p></div>',unsafe_allow_html=True)
    rs=tests(u["id"]); ms=[r["moisture"] for r in rs if r["moisture"] is not None]; ps=[r["protein"] for r in rs if r["protein"] is not None]
    a,b,c=st.columns(3); a.metric(tr("Saved tests"),len(rs)); b.metric(tr("Average moisture"),f"{np.mean(ms):.1f}%" if ms else "—"); c.metric(tr("Average protein"),f"{np.mean(ps):.1f}%" if ps else "—")
    st.subheader("System workflow")
    cols=st.columns(3)
    for i,x in enumerate(["1. Capture sample","2. Pre-process image","3. Visual screening","4. Enter measured values","5. Review guidance","6. Save to history"]):cols[i%3].info(x)
    st.warning("The camera feature is experimental. It cannot confirm fungi or mycotoxins; a low score does not prove feed is safe.")
elif page==tr("New Test"):
    st.title("📷 New Feed Test")
    st.write("Take a representative sample photo. Enter moisture and protein only if measured using suitable equipment or laboratory analysis.")
    with st.form("newtest"):
        feed=st.selectbox(tr("Feed type"),[tr("Cattle feed"),tr("Silage"),tr("Hay / fodder"),"Concentrate mixture",tr("Other")])
        src=st.radio(tr("Image source"),[tr("Camera"),tr("Upload")],horizontal=True)
        f=st.camera_input("Capture sample") if src==tr("Camera") else st.file_uploader("Upload sample image",type=["png","jpg","jpeg"])
        a,b,c=st.columns(3)
        m=a.number_input(tr("Measured moisture (%)"),0.0,100.0,0.0,.1)
        p=b.number_input(tr("Measured crude protein (%)"),0.0,100.0,0.0,.1)
        target=c.number_input(tr("Target crude protein (%)"),0.0,100.0,16.0,.5)
        notes=st.text_area(tr("Notes (optional)"))
        submit=st.form_submit_button(tr("Analyse and save test"),type="primary",use_container_width=True)
    if submit:
        score=None
        if f:
            try:
                im=Image.open(f).convert("RGB"); st.image(im,width=400); score=visual(im)
                st.metric("Visual anomaly indicator (not diagnosis)",f"{score:.1f}/100")
                st.warning("This colour/texture heuristic is not a trained fungal detector. A low score does not mean feed is safe.")
            except Exception as e:st.error(f"Could not process image: {e}")
        if m==0 and p==0:st.error("Enter at least one measured value before saving.")
        else:save(u["id"],feed,m or None,p or None,target or None,score,notes); st.success("Test saved to your account."); st.rerun()
elif page==tr("Test History"):
    st.title("🕒 My Test History"); rs=tests(u["id"])
    if not rs:st.info("No tests saved yet. Open New Test to begin.")
    else:
        for r in rs:
            with st.expander(f'{r["date"]} · {r["feed"]}'):
                a,b,c=st.columns(3); a.metric("Moisture",f'{r["moisture"]:.1f}%' if r["moisture"] is not None else "—"); b.metric("Protein",f'{r["protein"]:.1f}%' if r["protein"] is not None else "—"); c.metric("Visual indicator",f'{r["score"]:.1f}/100' if r["score"] is not None else "—")
                st.write("Target protein:",r["target"] if r["target"] is not None else "—"); st.write(r["notes"] or "")
        rows=[{"Date":r["date"],"Feed":r["feed"],"Moisture":r["moisture"],"Protein":r["protein"],"Target":r["target"],"Visual indicator":r["score"]} for r in rs]
        st.download_button(tr("Download my history as CSV"),pd.DataFrame(rows).to_csv(index=False).encode(),"feedwise_history.csv","text/csv")
elif page==tr("Nutritional Guide"):
    st.title("📘 Nutritional Guide")
    st.info("Protein targets vary with weight, age, lactation, pregnancy, milk yield, feed intake and the complete ration. There is no single percentage for every animal.")
    st.markdown("**Crude protein (CP)** is a feed-analysis measure, commonly estimated from nitrogen content. It is not the same as protein an animal can use.\n\n- Compare values on the same basis (such as dry matter).\n- Use a lab report or calibrated analyser for a reliable value.\n- Ask a qualified nutritionist to set the target.\n- Do not change feed based only on the image score.")
elif page==tr("Feed Recommendation"):
    st.title("💡 Feed Recommendation"); rs=tests(u["id"])
    if not rs:st.info("Save a test first to view guidance.")
    else:
        r=rs[0]
        if r["moisture"] is not None:
            if r["moisture"]>12:st.warning("Moisture is above the demo reference of 12%. The appropriate limit depends on feed type and storage conditions; verify against a relevant standard.")
            else:st.info("Moisture is at or below the demo reference; this alone does not establish safety.")
        if r["protein"] is not None and r["target"] is not None:
            d=r["protein"]-r["target"]
            if d<-.05:st.warning(f'Protein is {abs(d):.1f} percentage points below your entered target. Review the full ration with a nutritionist.')
            elif d>.05:st.info(f'Protein is {d:.1f} points above your entered target. Confirm both values use the same basis.')
            else:st.success("Measured protein matches the entered target; review the full ration as well.")
        if r["score"] is not None and r["score"]>=25:st.error("Image features were flagged. Inspect the batch and arrange appropriate testing if spoilage is suspected.")
        st.caption("Informational only. Do not use this application alone to decide feed safety or ration suitability.")
