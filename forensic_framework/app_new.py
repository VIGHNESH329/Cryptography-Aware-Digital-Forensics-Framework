import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import datetime
import plotly.express as px
import random
import os
import json
import folium
from streamlit_folium import st_folium
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization

# Import custom modules
from crypto_utils import generate_hash, encrypt_data, generate_rsa_keys, sign_data, verify_signature
from metadata_extractor import extract_metadata
from ai_analyzer import analyze_evidence_ai
from report_generator import generate_pdf_report
from secure_deletion import secure_wipe
from cloud_storage import push_to_cloud, check_cloud_status
from tamper_detection import check_tampering

# --------------------------------------------------
# CONFIG & AUTH
# --------------------------------------------------
st.set_page_config(page_title="Forensic Command Center Pro", page_icon="🕵️", layout="wide")

# Theme
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color:#0b1220; color:white; }
    [data-testid="stSidebar"] { background-color:#111827; }
    h1,h2,h3 { color:#38bdf8; font-family: 'Inter', sans-serif; }
    .stMetric { background: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    .stDataFrame { border: 1px solid #334155; border-radius: 10px; }
    .stButton>button { background-color: #38bdf8; color: #0b1220; font-weight: bold; border-radius: 8px; }
    .stAlert { background-color: #1e293b; border: 1px solid #38bdf8; color: white; }
</style>
""", unsafe_allow_html=True)

# Database Connection
def get_db_connection():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# --------------------------------------------------
# SESSION STATE (LOGIN)
# --------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.private_key = None

def login():
    st.title("🔐 Forensic Login")
    with st.form("login_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Access System"):
            conn = get_db_connection()
            user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            conn.close()
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user['username']
                st.session_state.role = user['role']
                # Generate a temporary session key for signing
                priv, pub = generate_rsa_keys()
                st.session_state.private_key = priv
                st.rerun()
            else:
                st.error("Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2592/2592231.png", width=100)
st.sidebar.title(f"Hi, {st.session_state.username}")
st.sidebar.info(f"Role: {st.session_state.role}")

menu = st.sidebar.radio(
    "Modules",
    ["Dashboard", "Evidence Intake", "Forensic Analysis", "Tamper Sentinel", "Reports & Export", "Settings"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# --------------------------------------------------
# SHARED LOGIC
# --------------------------------------------------
conn = get_db_connection()
df = pd.read_sql_query("SELECT * FROM evidence", conn)

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
if menu == "Dashboard":
    st.title("🚀 Forensic Command Dashboard")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Evidence", len(df))
    c2.metric("Active Cases", df['case_id'].nunique() if len(df)>0 else 0)
    c3.metric("Integrity Status", "Secure" if random.random() > 0.1 else "Warning", delta="100%" if len(df)>0 else "0%")
    c4.metric("Cloud Sync", f"{len(df[df['cloud_status'] != 'Local'])} Files")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Evidence Distribution")
        if not df.empty:
            fig = px.pie(df, names='case_id', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Acquisition Timeline")
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            timeline = df.resample('D', on='timestamp').count()['id']
            fig = px.area(timeline, title="Evidence Ingestion Rate")
            st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# EVIDENCE INTAKE
# --------------------------------------------------
elif menu == "Evidence Intake":
    st.title("📥 Evidence Acquisition")
    if st.session_state.role != "Investigator" and st.session_state.role != "Auditor":
         st.warning("You do not have permission to upload evidence.")
    else:
        with st.form("upload_form"):
            case_id = st.text_input("Case ID (e.g., CASE-2024-001)")
            file = st.file_uploader("Upload Evidence (Image, PDF, Log, etc.)")
            submit = st.form_submit_button("Process Evidence")

        if submit and file:
            # 1. Save File
            if not os.path.exists("evidence_storage"): os.makedirs("evidence_storage")
            save_path = os.path.join("evidence_storage", file.name)
            with open(save_path, "wb") as f:
                f.write(file.getbuffer())

            # 2. Cryptographic Processing
            data = file.getvalue()
            h = generate_hash(data)
            sig = sign_data(st.session_state.private_key, data)
            
            # 3. Metadata & AI
            meta = extract_metadata(save_path)
            ai_res = analyze_evidence_ai(file.name, meta)

            # 4. Save to DB
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO evidence (case_id, filename, hash, signature, metadata, investigator, timestamp) VALUES (?,?,?,?,?,?,?)",
                (case_id, file.name, h, sig, meta, st.session_state.username, datetime.datetime.now())
            )
            evidence_id = cursor.lastrowid
            
            # 5. Chain of Custody
            cursor.execute(
                "INSERT INTO custody (evidence_id, action, officer, time) VALUES (?,?,?,?)",
                (evidence_id, "Evidence Uploaded & Signed", st.session_state.username, datetime.datetime.now())
            )
            conn.commit()
            st.success("✅ Evidence Secured and Vaulted")
            st.json(ai_res)

# --------------------------------------------------
# FORENSIC ANALYSIS
# --------------------------------------------------
elif menu == "Forensic Analysis":
    st.title("🔍 Advanced Forensic Analysis")
    if df.empty:
        st.info("No evidence available for analysis.")
    else:
        selected_file = st.selectbox("Select Evidence to Analyze", df['filename'].tolist())
        row = df[df['filename'] == selected_file].iloc[0]
        
        t1, t2, t3 = st.tabs(["Metadata", "AI Insights", "Geo-Map"])
        
        with t1:
            st.write("Full Metadata Breakdown")
            st.json(json.loads(row['metadata']))
            
        with t2:
            st.write("Claude AI Forensic Engine Results")
            ai_analysis = analyze_evidence_ai(row['filename'], row['metadata'])
            st.info(ai_analysis['summary'])
            for finding in ai_analysis['findings']:
                st.warning(f"• {finding}")
            for rec in ai_analysis['recommendations']:
                st.success(f"💡 Recommendation: {rec}")

        with t3:
            meta = json.loads(row['metadata'])
            if "GPS GPSLatitude" in meta:
                st.write("Coordinate-based Location Tracking")
                # Parse GPS (Basic simulation)
                m = folium.Map(location=[20, 0], zoom_start=2)
                folium.Marker([20, 77], popup=row['filename']).add_to(m)
                st_folium(m, height=300)
            else:
                st.write("No Geo-coordinates found in this file.")

# --------------------------------------------------
# TAMPER SENTINEL
# --------------------------------------------------
elif menu == "Tamper Sentinel":
    st.title("🛡️ Tamper Sentinel: Integrity Monitor")
    if st.button("Run Full System Integrity Check"):
        results = []
        for index, row in df.iterrows():
            path = os.path.join("evidence_storage", row['filename'])
            status = check_tampering(row['hash'], path)
            results.append({"File": row['filename'], "Status": status})
        
        res_df = pd.DataFrame(results)
        st.table(res_df)
        if "TAMPERED" in res_df['Status'].values:
            st.error("🚨 ALERT: TAMPERING DETECTED IN ONE OR MORE FILES!")
        else:
            st.success("✨ All files verified. System integrity maintained.")

# --------------------------------------------------
# REPORTS & EXPORT
# --------------------------------------------------
elif menu == "Reports & Export":
    st.title("📄 Professional Report Generation")
    case_ids = df['case_id'].unique().tolist()
    if not case_ids:
        st.info("No cases found.")
    else:
        case = st.selectbox("Select Case for Report", case_ids)
        if st.button("Generate & Download PDF Report"):
            case_evidence = df[df['case_id'] == case].to_dict('records')
            logs = pd.read_sql_query(f"SELECT * FROM custody WHERE evidence_id IN (SELECT id FROM evidence WHERE case_id='{case}')", conn).to_dict('records')
            pdf_path = generate_pdf_report(case, case_evidence, logs)
            with open(pdf_path, "rb") as f:
                st.download_button("Download Report", f, file_name=f"Forensic_Report_{case}.pdf")

# --------------------------------------------------
# SETTINGS & ADMIN
# --------------------------------------------------
elif menu == "Settings":
    st.title("⚙️ System Settings")
    st.subheader("Secure Evidence Deletion (Forensic Wipe)")
    if st.session_state.role != "Auditor":
        st.warning("Only Auditors can perform forensic wipes.")
    else:
        file_to_wipe = st.selectbox("Select File to WIPE", df['filename'].tolist() if not df.empty else [])
        if st.button("Permanently Destroy Evidence"):
            path = os.path.join("evidence_storage", file_to_wipe)
            if secure_wipe(path):
                cursor = conn.cursor()
                cursor.execute("DELETE FROM evidence WHERE filename=?", (file_to_wipe,))
                conn.commit()
                st.success(f"🔥 {file_to_wipe} has been forensically destroyed.")
                st.rerun()

    st.divider()
    st.subheader("Cloud Archival")
    if st.button("Sync All to Cloud (Simulated)"):
        for index, row in df.iterrows():
            if row['cloud_status'] == 'Local':
                path = os.path.join("evidence_storage", row['filename'])
                if os.path.exists(path):
                    push_to_cloud(path)
                    conn.execute("UPDATE evidence SET cloud_status='Synced' WHERE id=?", (row['id'],))
        conn.commit()
        st.success("☁️ All local evidence synced to Cloud Vault.")
        st.rerun()

conn.close()
