import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# ===============================
# Config
# ===============================
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Policy Compliance Dashboard", layout="wide")
st.title("📊 Policy Compliance Dashboard")

# ===============================
# Upload Section
# ===============================
st.header("📤 Upload Policies")

col1, col2 = st.columns(2)

with col1:
    file_a = st.file_uploader("Upload Policy A", type=["pdf"])

with col2:
    file_b = st.file_uploader("Upload Policy B", type=["pdf"])

# ===============================
# Run Pipeline
# ===============================
if st.button("🚀 Run Full Pipeline"):

    if not file_a or not file_b:
        st.warning("⚠️ Please upload both files")
        st.stop()

    try:
        st.write("📤 Uploading...")
        requests.post(f"{BASE_URL}/upload/upload/", files={"file": file_a})
        requests.post(f"{BASE_URL}/upload/upload/", files={"file": file_b})

        st.write("📄 Parsing...")
        requests.post(f"{BASE_URL}/parse/parse/", params={"file_name": "BANK_POLICY.pdf"})
        requests.post(f"{BASE_URL}/parse/parse/", params={"file_name": "VENDOR_POLICY.pdf"})

        st.write("✂️ Segmenting...")
        requests.post(f"{BASE_URL}/segment/segment/", params={"file_name": "BANK_POLICY.pdf"})
        requests.post(f"{BASE_URL}/segment/segment/", params={"file_name": "VENDOR_POLICY.pdf"})

        st.write("🧠 Embedding...")
        requests.post(f"{BASE_URL}/embed/embed/", params={"file_name": "BANK_POLICY.pdf"})
        requests.post(f"{BASE_URL}/embed/embed/", params={"file_name": "VENDOR_POLICY.pdf"})

        st.write("⚖️ Comparing...")
        res = requests.post(
            f"{BASE_URL}/compare/compare/",
            params={
                "bank_file": "BANK_POLICY.pdf",
                "vendor_file": "VENDOR_POLICY.pdf"
            }
        )

        if res.status_code == 200:
            st.session_state["results"] = res.json()
            st.success("✅ Pipeline Completed")
        else:
            st.error(res.text)
            st.stop()

    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

# ===============================
# Show Results
# ===============================
if "results" in st.session_state:

    results = st.session_state["results"]
    summary = results["summary"]
    df = pd.DataFrame(results["alignment_matrix"])

    # ===============================
    # 🎨 Cards
    # ===============================
    st.markdown("""
    <style>
    .card {
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: white;
    }
    .blue { background: #007bff; }
    .green { background: #28a745; }
    .orange { background: #ffc107; color: black; }
    .red { background: #dc3545; }
    </style>
    """, unsafe_allow_html=True)

    st.header("📌 Executive Summary")

    if summary["overall_compliance"] >= 80:
        st.success("✅ High compliance")
    elif summary["overall_compliance"] >= 50:
        st.warning("⚠️ Moderate compliance")
    else:
        st.error("❌ Low compliance")

    # ===============================
    # 📊 Cards Row
    # ===============================
    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f'<div class="card blue">Overall<br>{summary["overall_compliance"]}%</div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="card green">Compliant<br>{summary["compliant"]}</div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="card orange">Partial<br>{summary["partial"]}</div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="card red">Missing<br>{summary["missing"]}</div>', unsafe_allow_html=True)

    st.markdown("### ")

    # ===============================
    # 📊 Charts (MEDIUM SIZE GRID)
    # ===============================
    st.header("📊 Analytics Dashboard")

    col1, col2 = st.columns(2)

    # Pie Chart
    with col1:
        st.subheader("Compliance Distribution")
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(
            [summary["compliant"], summary["partial"], summary["missing"]],
            labels=["Compliant", "Partial", "Missing"],
            autopct="%1.1f%%"
        )
        st.pyplot(fig)

    # Bar Chart
    with col2:
        st.subheader("Clause Status")
        fig, ax = plt.subplots(figsize=(4, 4))
        status_counts = df["status"].value_counts()
        ax.bar(status_counts.index, status_counts.values)
        st.pyplot(fig)

    # Second Row
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Risk Distribution")
        fig, ax = plt.subplots(figsize=(4, 4))
        risk_counts = df["risk"].value_counts()
        ax.bar(risk_counts.index, risk_counts.values)
        st.pyplot(fig)

    with col4:
        st.subheader("Score Distribution")
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.hist(df["combined_score"], bins=10)
        st.pyplot(fig)

    st.markdown("### ")

    # ===============================
    # 🚨 Critical Gaps
    # ===============================
    st.header("🚨 Critical Gaps")
    gaps = df[df["status"] != "Compliant"]
    st.dataframe(gaps, use_container_width=True)

    # ===============================
    # 📑 Full Table
    # ===============================
    st.header("📑 Clause Comparison")

    def highlight_row(row):
        if row["status"] == "Compliant":
            return ["background-color: #d4edda"] * len(row)
        elif row["status"] == "Partial":
            return ["background-color: #fff3cd"] * len(row)
        else:
            return ["background-color: #f8d7da"] * len(row)

    st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

    # ===============================
    # 💡 Recommendations
    # ===============================
    st.header("💡 Recommendations")

    recs = []
    for r in df["status"]:
        if r == "Missing":
            recs.append("Add missing compliance clauses")
        elif r == "Partial":
            recs.append("Improve alignment with bank policy")

    for r in set(recs):
        st.write("•", r)

    # ===============================
    # 📥 Download
    # ===============================
    st.header("📥 Export Report")

    st.download_button(
        "⬇️ Download CSV",
        df.to_csv(index=False),
        "policy_report.csv"
    )