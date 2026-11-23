import os
import streamlit as st
import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
import socket
import time
import requests
from urllib.parse import urlparse
from datetime import datetime

st.set_page_config(
    page_title="Real-Time NIDS Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS (WITH BRIGHT WHITE LABELS & SIDEBAR FIXES)
# =========================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0b1220 0%, #111827 45%, #0f172a 100%);
        color: #f8fafc;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
        font-family: "Segoe UI", sans-serif;
    }

    p, span, div {
        font-family: "Segoe UI", sans-serif;
    }

    div[data-testid="stMarkdownContainer"] p {
        color: #f1f5f9 !important;
    }

    /* =====================================================
       FIX: Make all Input & Selectbox Labels bright white
       ===================================================== */
    label, 
    label[data-testid="stWidgetLabel"],
    label[data-testid="stWidgetLabel"] p,
    label[data-testid="stWidgetLabel"] span {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* =====================================================
       FIX: Make all Sidebar text & keys bright and visible
       ===================================================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        border-right: 1px solid rgba(148,163,184,0.12);
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #e2e8f0 !important;
    }

    /* Highlight key names in sidebar (e.g., "Dataset Name:", "Type:") in soft blue */
    section[data-testid="stSidebar"] strong {
        color: #93c5fd !important;
    }

    /* =====================================================
       Inputs & Buttons Styling
       ===================================================== */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(15,23,42,0.95) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid rgba(148,163,184,0.3) !important;
    }

    .stTextInput input::placeholder {
        color: #94a3b8 !important;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(30,41,59,0.95), rgba(15,23,42,0.92));
        border: 1px solid rgba(148,163,184,0.18);
        border-radius: 24px;
        padding: 2rem 2rem 1.6rem 2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }

    .hero-title {
        font-size: 2.7rem;
        font-weight: 800;
        line-height: 1.15;
        color: #ffffff !important;
        margin-bottom: 0.35rem;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #cbd5e1 !important;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(30,41,59,0.75), rgba(15,23,42,0.9));
        border: 1px solid rgba(148,163,184,0.15);
        border-radius: 18px;
        padding: 1rem;
        text-align: left;
        min-height: 110px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.18);
    }

    .metric-label {
        font-size: 0.92rem;
        color: #94a3b8 !important;
        margin-bottom: 0.4rem;
        font-weight: 600;
    }

    .metric-value {
        font-size: 1.45rem;
        font-weight: 800;
        color: #ffffff !important;
        word-break: break-word;
    }

    .metric-sub {
        font-size: 0.85rem;
        color: #cbd5e1 !important;
        margin-top: 0.3rem;
    }

    .status-good {
        background: rgba(34,197,94,0.14);
        color: #bbf7d0 !important;
        border: 1px solid rgba(34,197,94,0.35);
        padding: 0.5rem 0.9rem;
        border-radius: 999px;
        display: inline-block;
        font-size: 0.9rem;
        font-weight: 700;
    }

    .status-bad {
        background: rgba(239,68,68,0.14);
        color: #fecaca !important;
        border: 1px solid rgba(239,68,68,0.35);
        padding: 0.5rem 0.9rem;
        border-radius: 999px;
        display: inline-block;
        font-size: 0.9rem;
        font-weight: 700;
    }

    .section-heading {
        font-size: 1.35rem;
        font-weight: 800;
        color: #f8fafc !important;
        margin: 0.25rem 0 0.85rem 0;
    }

    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.72rem 1.2rem !important;
        font-weight: 700 !important;
        width: 100%;
        box-shadow: 0 8px 20px rgba(37,99,235,0.28);
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #0f766e, #0d9488) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.72rem 1.2rem !important;
        font-weight: 700 !important;
        width: 100%;
    }

    .sidebar-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(148,163,184,0.16);
        border-radius: 16px;
        padding: 0.9rem;
        margin-bottom: 0.8rem;
    }

    .sidebar-title {
        font-size: 1.05rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        color: #ffffff !important;
    }

    .sidebar-subtitle {
        color: #cbd5e1 !important;
        font-size: 0.9rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 10px 18px;
        color: #e2e8f0;
        border: 1px solid rgba(148,163,184,0.12);
    }

    .stTabs [aria-selected="true"] {
        background: rgba(37,99,235,0.16) !important;
        color: #ffffff !important;
        border: 1px solid rgba(96,165,250,0.32) !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(148,163,184,0.10);
    }

    /* =====================================================
       FIX: Alert boxes (st.success, st.error, st.info)
       ===================================================== */
    div[data-testid="stAlert"] {
        background-color: #0f172a !important;
        border-radius: 14px !important;
        border: 1px solid rgba(148, 163, 184, 0.25) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
    }

    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span,
    div[data-testid="stAlert"] div {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    div[data-testid="stAlert"] a {
        color: #60a5fa !important;
        text-decoration: underline !important;
    }

    /* Success box styling */
    div[data-testid="stAlert"]:has([data-testid="stNotificationContentSuccess"]) {
        background-color: rgba(22, 101, 52, 0.35) !important;
        border: 1px solid rgba(34, 197, 94, 0.5) !important;
    }

    /* Error box styling */
    div[data-testid="stAlert"]:has([data-testid="stNotificationContentError"]) {
        background-color: rgba(153, 27, 27, 0.35) !important;
        border: 1px solid rgba(239, 68, 68, 0.5) !important;
    }

    /* =====================================================
       FIX: st.json and code display blocks
       ===================================================== */
    div[data-testid="stJson"],
    div[data-testid="stJson"] pre,
    div[data-testid="stJson"] div {
        background-color: #0f172a !important;
        border-radius: 12px !important;
    }

    div[data-testid="stJson"] {
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        padding: 0.75rem 1rem !important;
    }

    div[data-testid="stJson"] span {
        font-family: "Consolas", "Courier New", monospace !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATASET + MODEL CONFIG
# =========================================================
DATASET_CONFIG = {
    "NSL-KDD": {
        "info": {
            "Dataset Name": "NSL-KDD",
            "Type": "Intrusion Detection Benchmark Dataset",
            "Target": "Normal vs Attack",
            "Common Attacks": "DoS, Probe, R2L, U2R",
            "Use Case": "Classical benchmark for network intrusion detection"
        },
        "models": {
            "CNN-LSTM": {
                "model": "nsl_CNN-LSTM.h5",
                "features": "cnn_lstm_feature_columns.pkl",
                "reshape": "cnn_lstm_reshape_config.pkl",
                "type": "deep_learning"
            },
            "RNN": {
                "model": "nsl_rnn.h5",
                "features": "rnn_feature_columns.pkl",
                "reshape": "rnn_reshape_config.pkl",
                "type": "deep_learning"
            },
            "NN": {
                "model": "nsl_nn.h5",
                "features": "nn_feature_columns.pkl",
                "reshape": None,
                "type": "deep_learning"
            },
            "CRNN": {
                "model": "nsl_crnn.h5",
                "features": "crnn_feature_columns.pkl",
                "reshape": "crnn_reshape_config.pkl",
                "type": "deep_learning"
            },
            "FFNN": {
                "model": "nsl_FFNN.h5" if os.path.exists("nsl_FFNN.h5") else "nsl_ffnn.h5",
                "features": "ffnn_feature_columns.pkl",
                "reshape": None,
                "type": "deep_learning"
            },
            "LR": {
                "model": "nsl_lr.pkl",
                "features": "lr_feature_columns.pkl",
                "reshape": None,
                "type": "machine_learning"
            },
            "GNB": {
                "model": "nsl_gnb.pkl",
                "features": "gnb_feature_columns.pkl",
                "reshape": None,
                "type": "machine_learning"
            },
            "RF": {
                "model": "nsl_rf.pkl",
                "features": "rf_feature_columns.pkl",
                "reshape": None,
                "type": "machine_learning"
            },
            "SVM": {
                "model": "nsl_svm.pkl",
                "features": "svm_feature_columns.pkl",
                "reshape": None,
                "type": "machine_learning"
            },
            "DT": {
                "model": "nsl_dt.pkl",
                "features": "dt_feature_columns.pkl",
                "reshape": None,
                "type": "machine_learning"
            }
        }
    },
    "UNSW-NB15": {
        "info": {
            "Dataset Name": "UNSW-NB15",
            "Type": "Modern Network Intrusion Dataset",
            "Target": "Normal vs Attack",
            "Common Attacks": "Fuzzers, Exploits, DoS, Reconnaissance, Worms",
            "Use Case": "Modern network traffic analysis and IDS benchmarking"
        },
        "models": {
            "CNN-LSTM": {
                "model": "unsw_CNN-LSTM.h5",
                "features": "unsw_cnn_lstm_feature_columns.pkl",
                "reshape": "unsw_cnn_lstm_reshape_config.pkl",
                "type": "deep_learning"
            },
            "NN": {
                "model": "unsw_nn_model.h5",
                "features": "unsw_nn_feature_columns.pkl",
                "reshape": None,
                "type": "deep_learning"
            },
            "FFNN": {
                "model": "unsw_model_ffnn.h5",
                "features": "unsw_ffnn_feature_columns.pkl",
                "reshape": None,
                "type": "deep_learning"
            },
            "CRNN": {
                "model": "unsw_model_crnn.h5",
                "features": "unsw_crnn_feature_columns.pkl",
                "reshape": "unsw_crnn_reshape_config.pkl",
                "type": "deep_learning"
            },
            "LR": {
                "model": "unsw_lr.pkl",
                "features": "unsw_lr_feature_columns.pkl",
                "reshape": None,
                "type": "machine_learning"
            },
            "RF": {
                "model": "unsw_rf.pkl",
                "features": "unsw_rf_feature_columns.pkl",
                "reshape": None,
                "type": "machine_learning"
            },
            "SVM": {
                "model": "unsw_svm.pkl",
                "features": "unsw_svm_feature_columns.pkl",
                "reshape": None,
                "type": "machine_learning"
            },
            "DT": {
                "model": "unsw_dt.pkl",
                "features": "unsw_dt_feature_columns.pkl",
                "reshape": None,
                "type": "machine_learning"
            }
        }
    }
}

# =========================================================
# HELPERS
# =========================================================
@st.cache_resource
def load_model_file(path, model_type):
    if model_type == "deep_learning":
        return tf.keras.models.load_model(path)
    if model_type == "machine_learning":
        return joblib.load(path)
    raise ValueError(f"Unsupported model type: {model_type}")

@st.cache_data
def load_pickle_file(path):
    return joblib.load(path)

def safe_get(url, timeout=10):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    response = requests.get(url, timeout=timeout)
    return url, response

def extract_real_parameters(url, feature_columns, dataset_name, timeout_sec=10):
    params = {col: 0.0 for col in feature_columns}

    url, response = safe_get(url, timeout=timeout_sec)
    parsed = urlparse(url)
    domain = parsed.netloc if parsed.netloc else parsed.path

    start_time = time.time()
    _ = requests.get(url, timeout=timeout_sec)
    end_time = time.time()

    response_time = end_time - start_time
    response_size = len(response.content)
    status_code = response.status_code

    try:
        ip_address = socket.gethostbyname(domain)
    except Exception:
        ip_address = "0.0.0.0"

    dst_port = 443.0 if parsed.scheme == "https" else 80.0

    common_values = {
        "dur": response_time,
        "sbytes": response_size,
        "dbytes": response_size,
        "sttl": 64.0,
        "dttl": 64.0,
        "sloss": 0.0,
        "dloss": 0.0,
        "sinpkt": response_time,
        "dinpkt": response_time,
        "sjit": 0.0,
        "djit": 0.0,
        "swin": 255.0,
        "stcpb": 1000.0,
        "dtcpb": 1000.0,
        "dwin": 255.0,
        "tcprtt": response_time / 2 if response_time > 0 else 0.0,
        "synack": response_time / 4 if response_time > 0 else 0.0,
        "ackdat": response_time / 4 if response_time > 0 else 0.0,
        "smean": response_size,
        "dmean": response_size,
        "trans_depth": 1.0,
        "response_body_len": response_size,
        "ct_srv_src": 1.0,
        "ct_state_ttl": 1.0,
        "ct_dst_ltm": 1.0,
        "ct_src_dport_ltm": 1.0,
        "ct_dst_sport_ltm": 1.0,
        "ct_dst_src_ltm": 1.0,
        "is_ftp_login": 0.0,
        "ct_ftp_cmd": 0.0,
        "ct_flw_http_mthd": 1.0,
        "ct_src_ltm": 1.0,
        "ct_srv_dst": 1.0,
        "is_sm_ips_ports": 0.0,
        "service": 0.0,
        "flag": 0.0,
        "src_bytes": response_size,
        "dst_bytes": response_size,
        "count": 1.0,
        "srv_count": 1.0
    }

    for col in feature_columns:
        params[col] = float(common_values.get(col, 0.0))

    extra_info = {
        "Dataset": dataset_name,
        "Resolved IP": ip_address,
        "HTTP Status Code": status_code,
        "Destination Port": dst_port,
        "Response Time": round(response_time, 4),
        "Response Size": response_size
    }

    return params, extra_info

def predict_with_model(model, input_data, model_type, reshape_config=None):
    if model_type == "deep_learning":
        if reshape_config is not None:
            expected_size = reshape_config["timesteps"] * reshape_config["features_per_step"]

            if input_data.shape[1] != expected_size:
                raise ValueError(
                    f"Feature mismatch → Model expects {expected_size} features but got {input_data.shape[1]}"
                )

            input_data = input_data.reshape(
                (input_data.shape[0], reshape_config["timesteps"], reshape_config["features_per_step"])
            )

        prediction = model.predict(input_data, verbose=0)
        score = float(prediction[0][0])
        predicted_class = int(score > 0.5)
        return score, predicted_class

    if model_type == "machine_learning":
        prediction = model.predict(input_data)

        if hasattr(model, "predict_proba"):
            score = float(model.predict_proba(input_data)[0][1])
        elif hasattr(model, "decision_function"):
            score = float(model.decision_function(input_data)[0])
        else:
            score = float(prediction[0])

        predicted_class = int(prediction[0])
        return score, predicted_class

    raise ValueError(f"Unsupported model type: {model_type}")

def build_result_row(timestamp, dataset_name, model_name, target, score, result):
    return {
        "Time": timestamp,
        "Dataset": dataset_name,
        "Model": model_name,
        "Target": target,
        "Score": round(float(score), 4),
        "Result": result
    }

# =========================================================
# SESSION STATE
# =========================================================
if "history" not in st.session_state:
    st.session_state.history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-card">
            <div class="sidebar-title">NIDS Console</div>
            <div class="sidebar-subtitle">
                Choose the active dataset and model, then run analysis against a live target.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Defaults to index=0 (NSL-KDD) because your folder contains the NSL models
    selected_dataset = st.selectbox(
        "Active Dataset",
        list(DATASET_CONFIG.keys()),
        index=0
    )

    if selected_dataset == "NSL-KDD":
        st.markdown("""
            <div class="sidebar-card">
                <div class="sidebar-title">📁 NSL-KDD</div>
                <div class="sidebar-subtitle">
                    Benchmark dataset for classical intrusion detection research.
                </div>
            </div>
        """, unsafe_allow_html=True)

        for k, v in DATASET_CONFIG["NSL-KDD"]["info"].items():
            st.write(f"**{k}:** {v}")

        selected_model_name = st.selectbox(
            "NSL-KDD Model",
            list(DATASET_CONFIG["NSL-KDD"]["models"].keys()),
            key="nsl_model_select"
        )

    else:
        st.markdown("""
            <div class="sidebar-card">
                <div class="sidebar-title">📁 UNSW-NB15</div>
                <div class="sidebar-subtitle">
                    Modern traffic dataset for broader intrusion analysis.
                </div>
            </div>
        """, unsafe_allow_html=True)

        for k, v in DATASET_CONFIG["UNSW-NB15"]["info"].items():
            st.write(f"**{k}:** {v}")

        selected_model_name = st.selectbox(
            "UNSW-NB15 Model",
            list(DATASET_CONFIG["UNSW-NB15"]["models"].keys()),
            key="unsw_model_select"
        )

    st.markdown("""
        <div class="sidebar-card">
            <div class="sidebar-title">Operational Notes</div>
            <div class="sidebar-subtitle">
                • ML models use <b>.pkl</b><br>
                • DL models use <b>.h5</b><br>
                • Keep feature files with the app<br>
                • Use reachable domains or URLs
            </div>
        </div>
    """, unsafe_allow_html=True)


# =========================================================
# MODEL CONFIG SETUP
# =========================================================
selected_model_config = DATASET_CONFIG[selected_dataset]["models"][selected_model_name]
model_type = selected_model_config["type"]

model_path = selected_model_config["model"]
features_path = selected_model_config["features"]
reshape_path = selected_model_config["reshape"]

if not os.path.exists(model_path):
    st.error(f"Model file not found: {model_path}")
    st.stop()

if not os.path.exists(features_path):
    st.error(f"Feature file not found: {features_path}")
    st.stop()

if model_type == "deep_learning" and reshape_path is not None and not os.path.exists(reshape_path):
    st.error(f"Reshape config file not found: {reshape_path}")
    st.stop()

try:
    model = load_model_file(model_path, model_type)
    feature_columns = load_pickle_file(features_path)

    if model_type == "deep_learning" and reshape_path is not None:
        reshape_config = load_pickle_file(reshape_path)
    else:
        reshape_config = None

except Exception as load_error:
    st.error(f"Model loading error: {load_error}")
    st.stop()

# =========================================================
# HERO SECTION
# =========================================================
st.markdown("""
<div class="hero-card">
    <div class="hero-title">🛡️ Network Intrusion Detection System</div>
    <div class="hero-subtitle">
        Advanced machine learning and deep learning based dashboard for analyzing network targets and detecting suspicious traffic patterns.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# OVERVIEW METRICS
# =========================================================
overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

with overview_col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Selected Dataset</div>
            <div class="metric-value">{selected_dataset}</div>
            <div class="metric-sub">Benchmark source</div>
        </div>
    """, unsafe_allow_html=True)

with overview_col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Selected Model</div>
            <div class="metric-value">{selected_model_name}</div>
            <div class="metric-sub">{model_type.replace("_", " ").title()}</div>
        </div>
    """, unsafe_allow_html=True)

with overview_col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Feature Count</div>
            <div class="metric-value">{len(feature_columns)}</div>
            <div class="metric-sub">Input variables required</div>
        </div>
    """, unsafe_allow_html=True)

with overview_col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">History Records</div>
            <div class="metric-value">{len(st.session_state.history)}</div>
            <div class="metric-sub">Stored runs</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("")

# =========================================================
# TARGET CONFIGURATION
# =========================================================
st.markdown('<div class="section-heading">📍 Network Target Configuration</div>', unsafe_allow_html=True)

input_col1, input_col2, input_col3 = st.columns([3.2, 1, 1])

with input_col1:
    network_link = st.text_input(
        "Enter Target (Domain, IP, or URL)",
        placeholder="e.g., google.com, 192.168.1.1, https://example.com"
    )

with input_col2:
    packets_to_capture = st.number_input(
        "Packets",
        min_value=1,
        max_value=1000,
        value=100,
        step=1
    )

with input_col3:
    timeout_sec = st.number_input(
        "Timeout (sec)",
        min_value=1,
        max_value=300,
        value=30,
        step=1
    )

action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    analyze_clicked = st.button("🔎 Analyze Target")

with action_col2:
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.session_state.last_result = None
        st.success("History cleared.")

with action_col3:
    history_df_export = pd.DataFrame(st.session_state.history) if st.session_state.history else pd.DataFrame()
    st.download_button(
        label="📤 Export Results",
        data=history_df_export.to_csv(index=False).encode("utf-8"),
        file_name="nids_results.csv",
        mime="text/csv"
    )

st.divider()

# =========================================================
# ANALYSIS
# =========================================================
if analyze_clicked:
    if network_link.strip() == "":
        st.warning("Please enter a target URL, IP, or domain.")
    else:
        try:
            with st.spinner("Analyzing target and extracting network parameters..."):
                params, extra_info = extract_real_parameters(
                    network_link,
                    feature_columns,
                    selected_dataset,
                    timeout_sec=timeout_sec
                )

                input_data = np.array([[params[col] for col in feature_columns]], dtype=np.float32)

                score, predicted_class = predict_with_model(
                    model,
                    input_data,
                    model_type,
                    reshape_config
                )

            result_text = "Attack Detected" if predicted_class == 1 else "Normal Traffic"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            result_payload = build_result_row(
                timestamp=timestamp,
                dataset_name=selected_dataset,
                model_name=selected_model_name,
                target=network_link,
                score=score,
                result=result_text
            )

            st.session_state.history.append(result_payload)
            st.session_state.last_result = {
                "params": params,
                "extra_info": extra_info,
                "score": score,
                "predicted_class": predicted_class,
                "result_text": result_text,
                "timestamp": timestamp,
                "target": network_link,
                "dataset": selected_dataset,
                "model_name": selected_model_name
            }

        except Exception as e:
            st.error(f"Error analyzing target: {e}")

# =========================================================
# LAST RESULT DISPLAY
# =========================================================
if st.session_state.last_result is not None:
    res = st.session_state.last_result
    params = res["params"]
    extra_info = res["extra_info"]
    score = res["score"]
    predicted_class = res["predicted_class"]
    result_text = res["result_text"]

    st.markdown('<div class="section-heading">🧪 Latest Analysis Result</div>', unsafe_allow_html=True)

    result_col1, result_col2 = st.columns(2)

    with result_col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Response Time</div>
                <div class="metric-value">{extra_info["Response Time"]} sec</div>
                <div class="metric-sub">Observed latency</div>
            </div>
        """, unsafe_allow_html=True)

    with result_col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">HTTP Status</div>
                <div class="metric-value">{extra_info["HTTP Status Code"]}</div>
                <div class="metric-sub">Target response code</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    if predicted_class == 1:
        st.markdown('<div class="status-bad">⚠️ Threat Classification: Attack Detected</div>', unsafe_allow_html=True)
        st.error(f"Potential malicious or abnormal traffic detected for target: {res['target']}")
    else:
        st.markdown('<div class="status-good">✅ Threat Classification: Normal Traffic</div>', unsafe_allow_html=True)
        st.success(f"Traffic appears normal for target: {res['target']}")

    st.markdown("")

    try:
        progress_score = float(score)
        if progress_score < 0:
            progress_score = 0.0
        elif progress_score > 1:
            progress_score = 1.0
    except Exception:
        progress_score = 0.0

    st.progress(progress_score)
    st.write(f"**Prediction Score:** `{score:.4f}`")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌐 Network Details",
        "📊 Extracted Parameters",
        "📋 Summary",
        "📈 Statistics"
    ])

    with tab1:
        st.json(extra_info)

    with tab2:
        params_df = pd.DataFrame(params.items(), columns=["Parameter", "Value"])
        st.dataframe(params_df, use_container_width=True, height=420)

    with tab3:
        if st.session_state.history:
            history_df = pd.DataFrame(st.session_state.history)

            st.markdown("### 🔍 View Filtered History")
            filter_option = st.selectbox(
                "Filter by Result",
                ["All", "Attack Detected", "Normal Traffic"],
                key="summary_filter_option"
            )

            if filter_option == "All":
                display_df = history_df.copy()
            else:
                display_df = history_df[history_df["Result"] == filter_option]

            st.dataframe(display_df, use_container_width=True, height=320)
        else:
            summary_df = pd.DataFrame([{
                "Time": res["timestamp"],
                "Target": res["target"],
                "Prediction Score": round(float(score), 4),
                "Result": result_text
            }])
            st.dataframe(summary_df, use_container_width=True)

    with tab4:
        if st.session_state.history:
            history_df = pd.DataFrame(st.session_state.history)

            attacks = int((history_df["Result"] == "Attack Detected").sum())
            normal = int((history_df["Result"] == "Normal Traffic").sum())

            hist_col1, hist_col2, hist_col3, hist_col4 = st.columns(4)

            with hist_col1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Analyses</div>
                        <div class="metric-value">{len(history_df)}</div>
                        <div class="metric-sub">All recorded runs</div>
                    </div>
                """, unsafe_allow_html=True)

            with hist_col2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Attack Alerts</div>
                        <div class="metric-value">{attacks}</div>
                        <div class="metric-sub">Potential threats</div>
                    </div>
                """, unsafe_allow_html=True)

            with hist_col3:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Normal Results</div>
                        <div class="metric-value">{normal}</div>
                        <div class="metric-sub">Benign classifications</div>
                    </div>
                """, unsafe_allow_html=True)

            with hist_col4:
                avg_score = round(float(history_df["Score"].mean()), 4) if not history_df.empty else 0.0
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Average Score</div>
                        <div class="metric-value">{avg_score}</div>
                        <div class="metric-sub">Mean prediction score</div>
                    </div>
                """, unsafe_allow_html=True)

            status_counts = history_df["Result"].value_counts()

            st.markdown("#### 📊 Result Distribution")
            st.bar_chart(status_counts)

            st.markdown("")

            st.markdown("#### 📋 Detection Summary")

            summary_stats_df = pd.DataFrame({
                "Metric": [
                    "Total Runs",
                    "Attack Alerts",
                    "Normal Results",
                    "Average Score"
                ],
                "Value": [
                    len(history_df),
                    attacks,
                    normal,
                    avg_score
                ]
            })

            st.dataframe(summary_stats_df, use_container_width=True, height=220)
        else:
            st.info("No analysis history available yet.")