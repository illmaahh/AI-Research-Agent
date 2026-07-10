# 🔬 AI Research Agent

An AI-powered research assistant that helps students, researchers, and professionals analyze academic research papers using **IBM Granite** and **IBM watsonx.ai**.

The application enables users to upload research papers, generate structured AI summaries, ask context-aware questions using Retrieval-Augmented Generation (RAG), generate citations, and explore research insights through a clean and interactive interface.

---

## ✨ Features

- 📄 Upload and analyze research papers (PDF)
- 🤖 AI-powered academic summarization
- 💬 Context-aware Research Q&A (RAG)
- 📚 Automatic citation generation
- 📊 Interactive research dashboard
- 🔍 PDF text extraction
- ⚡ Fast and intuitive Streamlit interface
- ☁️ IBM Granite integration through watsonx.ai

---

## 📸 Application Preview

> *(Add screenshots after uploading them to the repository.)*

### 🏠 Home Page

<img src="assets/home.png" width="900"/>

### 🤖 AI Research Agent

<img src="assets/research-agent.png" width="900"/>

### 📊 Dashboard

<img src="assets/dashboard.png" width="900"/>

### ℹ️ About

<img src="assets/about.png" width="900"/>

---

# 🚀 Workflow

```
Upload PDF
      │
      ▼
Extract Text
      │
      ▼
Build RAG Index
      │
      ▼
IBM Granite
      │
      ├────────► AI Summary
      │
      ├────────► Research Q&A
      │
      └────────► Citation Generation
```

---

# 🛠️ Tech Stack

### Frontend

- Streamlit

### Backend

- Python

### Artificial Intelligence

- IBM Granite
- IBM watsonx.ai

### Document Processing

- PyMuPDF
- pypdf

### Vector Search

- FAISS

### Environment

- IBM Cloud

---

# 📂 Project Structure

```
AI-Research-Agent/
│
├── pages/
│   ├── 1_Home.py
│   ├── 2_Dashboard.py
│   └── 3_About.py
│
├── utils/
│   ├── ibm_client.py
│   ├── pdf_parser.py
│   └── vector_store.py
│
├── uploaded_papers/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/illmaahh/AI-Research-Agent.git

cd AI-Research-Agent
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file using `.env.example`.

```env
IBM_API_KEY=YOUR_IBM_API_KEY
IBM_PROJECT_ID=YOUR_PROJECT_ID
IBM_URL=https://us-south.ml.cloud.ibm.com
```

---

## Run the Application

```bash
streamlit run app.py
```

---

# 📖 How to Use

1. Launch the application.
2. Upload a research paper in PDF format.
3. Wait while the document is processed.
4. Generate an AI summary.
5. Ask questions about the uploaded paper.
6. Generate academic citations.
7. Explore document insights from the dashboard.

---

# 📊 Key Features

### 📄 PDF Analysis

- Upload academic papers
- Extract complete document text
- Intelligent document processing

### 🤖 AI Summarization

- Research objective
- Methodology
- Key findings
- Results
- Conclusion

### 💬 Research Q&A

- Retrieval-Augmented Generation (RAG)
- Context-aware responses
- Answers grounded in uploaded research paper

### 📚 Citation Generator

- IEEE Format
- APA Format

### 📊 Dashboard

- Document statistics
- Reading time estimation
- Word count
- Research insights

---

# 🔮 Future Improvements

- Multi-document analysis
- Literature review generation
- Semantic search across multiple papers
- Export summaries as PDF
- Research recommendation engine
- Interactive visual analytics
- Citation export (BibTeX, MLA, Chicago)

---

# 🎓 Internship

This project was developed during the

**AICTE – Edunet Foundation – IBM SkillsBuild Internship 2026**

using

- IBM Granite
- IBM watsonx.ai
- IBM Cloud

---

# 👩‍💻 Author

## Ilma Rasheed

Computer Science Engineering Student

GitHub:
https://github.com/illmaahh

LinkedIn:
(https://www.linkedin.com/in/ilmah-rasheed-299710251/)

---

# ⭐ Support

If you found this project helpful, please consider giving it a ⭐ on GitHub.

---

# 📄 License

This project is intended for educational and academic purposes.
