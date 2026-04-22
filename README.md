# 📊 Policy Compliance using LLM

An AI-powered Policy Compliance System that compares Bank vs Vendor policies using a hybrid approach of:

✅ Regex-based keyword matching
🤖 LLM-based semantic comparison (Mistral)
🧠 Vector search using Pinecone
📊 Risk scoring & gap detection
📈 Interactive dashboard (Streamlit)

🚀 Key Features

1. Hybrid Clause Comparison
Combines Regex + LLM
Captures:
Mandatory terms (must, shall)
Security intent
Semantic meaning

2. Semantic Search (Vector DB)
Uses embeddings + Pinecone
Finds closest matching clauses
Topic-aware filtering:
Security
Risk
Access
Incident
Business Continuity

3. Compliance Classification

Each clause is classified as:

✅ Compliant
⚠️ Partial
❌ Missing
🚨 4. Gap Detection

Identifies:

Missing requirements
Weak controls
Incomplete clauses
📊 5. Risk Scoring

Based on:

LLM result
Confidence score
Similarity score
Status Risk
Non-Compliant 🔴 High
Partial 🟠 Medium
Compliant 🟢 Low

📈 6. Interactive Dashboard (Streamlit)
Executive summary
Charts:
Compliance distribution
Risk distribution
Clause-level comparison table
CSV export

Project Architecture
policy-compliance-system/
│
├── app/
│   ├── api/                  # FastAPI routes
│   │   ├── upload.py
│   │   ├── parse.py
│   │   ├── segment.py
│   │   ├── embed.py
│   │   ├── compare.py
│   │
│   ├── core/
│   │   └── config.py        # Environment settings
│   │
│   ├── models/
│   │   └── schema.py        # Request/Response schemas
│   │
│   ├── services/            # Core logic
│   │   ├── pdf_parser.py
│   │   ├── clause_splitter.py
│   │   ├── embedding_engine.py
│   │   ├── pinecone_db.py
│   │   ├── semantic_search.py
│   │   ├── regex_comparator.py
│   │   ├── llm_comparator.py
│   │   ├── llm_keyword_extractor.py
│   │   ├── gap_detector.py
│   │   ├── risk_scorer.py
│   │   ├── compliance_scorer.py
│   │   └── topic_detector.py
│   │
│   ├── utils/
│   │   ├── file_utils.py
│   │   └── text_cleaner.py
│
├── data/
│   ├── raw/                 # Input PDFs
│   ├── parsed/              # Parsed JSON
│   ├── segmented/           # Clause-level data
│   └── results/             # Final output
│
├── scripts/
│   └── run_pipeline.py      # Full pipeline automation
│
├── ui/
│   └── app.py               # Streamlit dashboard
│
├── main.py                  # FastAPI entry point
├── requirements.txt
├── .env
└── README.md

⚙️ Installation
1️⃣ Clone Repository
git clone <https://github.com/your-username/policy-compliance-system.git>
cd policy-compliance-system

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Setup Environment Variables

Create .env file:

MISTRAL_API_KEY=your_mistral_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=your_index_name

▶️ Running the Project
🔹 Start FastAPI Backend
uvicorn main:app --reload

🔹 Run Streamlit UI
streamlit run ui/app.py

🔹 Run Full Pipeline (CLI)
python scripts/run_pipeline.py

🔄 Workflow Pipeline
PDF Upload
   ↓
Parsing
   ↓
Clause Segmentation
   ↓
Embedding Generation
   ↓
Pinecone Storage
   ↓
Semantic Search
   ↓
Regex Comparison
   ↓
LLM Comparison
   ↓
Gap Detection
   ↓
Risk Scoring
   ↓
Final Report

📊 Sample Output
{
  "overall_compliance": 75,
  "compliant": 8,
  "partial": 5,
  "missing": 1,
  "critical_gaps": 1
}

Core Logic Highlights
🔹 Hybrid Similarity
local_score = 0.7 *keyword_score + 0.3* text_score
🔹 Smart Fallback
No keyword match → still assigns base similarity
Uses LLM for semantic understanding
🔹 Risk Engine
if status == "Non-Compliant":
    return "High"

Output Files
File Description
comparison.json Clause-level comparison
final_results.json Summary + results
report.xlsx Exported report

Technologies Used
Backend: FastAPI
Frontend: Streamlit
LLM: Mistral
Vector DB: Pinecone
NLP: Sentence Transformers
Visualization: Matplotlib

💡 Use Cases
🏦 Bank vs Vendor policy validation
📜 Regulatory compliance audits
🔐 Information security gap analysis
🧾 Third-party risk assessment

🔮 Future Improvements
✅ Multi-policy comparison
✅ Explainable AI insights
✅ Auto-remediation suggestions
✅ Role-based dashboards
✅ Real-time compliance monitoring
