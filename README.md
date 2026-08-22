# 🤖 AI Job Research & Matching Platform

An AI-powered job research and matching platform that helps users discover relevant job opportunities through **natural-language search, semantic matching, personalized recommendations, and resume-based job matching**.

The platform combines a **React/Vite frontend**, **FastAPI backend**, **PostgreSQL**, and **Qdrant vector search** to provide an intelligent and personalized job discovery experience.

---

## 📌 Overview

Traditional job portals primarily rely on keyword-based searches.

This project makes job discovery more intelligent by allowing users to describe their requirements naturally.

For example:

> Find remote Python Data Scientist jobs with Machine Learning experience.

Instead of relying only on exact keywords, the system processes the user's intent, performs semantic retrieval, evaluates multiple matching factors, and returns relevant job opportunities.

### The platform provides four core experiences:

- 🔎 **Job Search**
- 🤖 **AI Job Assistant**
- 🎯 **Personalized Recommendations**
- 📄 **Resume Match**

---

# ✨ Key Features

## 🔎 1. Job Search

The Jobs section allows users to browse and search through a large collection of job opportunities.

Users can search using information such as:

- Job title
- Company
- Location
- Skills
- Experience
- Employment type
- Other job-related attributes

The backend retrieves structured job information from PostgreSQL.

---

## 🤖 2. AI Job Assistant

The AI Job Assistant allows users to search for jobs using natural language.

### Example

```text
Find remote Python developer jobs
```

Another example:

```text
Show me Data Scientist jobs in Bengaluru
```

The system interprets the user's query and retrieves relevant opportunities.

### Capabilities

- Natural-language search
- Intent understanding
- Semantic matching
- Relevant job retrieval
- Ranked job results

---

## 🧠 3. Semantic Job Matching

The platform goes beyond traditional keyword matching by using semantic similarity.

For example:

```text
Machine Learning Engineer
```

can be considered relevant to:

```text
AI Engineer with Deep Learning experience
```

even when the exact keywords are different.

### Semantic Search Flow

```text
User Query
    ↓
Query Processing
    ↓
Embedding Generation
    ↓
Qdrant Vector Search
    ↓
Relevant Jobs
    ↓
Ranking
    ↓
Results
```

This allows the application to retrieve jobs based on **meaning and relevance**, rather than relying only on exact keyword matches.

---

## 🎯 4. Personalized Recommendations

Users can describe the type of opportunity they are looking for.

Example:

```text
Python Data Scientist with Machine Learning experience in Bengaluru
```

The system retrieves and ranks jobs based on multiple matching factors.

### Matching Factors

- Semantic similarity
- Skill match
- Role match
- Location match
- Overall relevance

Example:

```text
AI Match       86%
Semantic       82%
Skill          90%
Role           88%
Location       85%
```

---

## 📄 5. Resume Match

Users can upload their resume and receive relevant job recommendations.

### Supported Formats

- PDF
- DOCX

The system extracts resume content and uses it to identify suitable opportunities based on:

- Skills
- Experience
- Role
- Location
- Overall profile

### Resume Matching Flow

```text
Resume Upload
      ↓
FastAPI Upload API
      ↓
PDF / DOCX Text Extraction
      ↓
Resume Analysis
      ↓
Job Matching
      ↓
Ranking
      ↓
Relevant Job Recommendations
```

---

# 🏗️ System Architecture

```text
                         ┌───────────────────┐
                         │       USER        │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │  React + Vite UI  │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │    FastAPI API    │
                         │      Backend      │
                         └─────────┬─────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
                 ▼                 ▼                 ▼
        ┌────────────────┐ ┌──────────────┐ ┌────────────────┐
        │  PostgreSQL    │ │    Qdrant    │ │ Resume Parser  │
        │                │ │              │ │                │
        │ Structured Job │ │   Vector     │ │ PDF / DOCX     │
        │     Data       │ │  Embeddings  │ │ Text Extraction│
        └───────┬────────┘ └──────┬───────┘ └───────┬────────┘
                │                 │                 │
                └─────────────────┼─────────────────┘
                                  ▼
                         ┌───────────────────┐
                         │ Matching & Ranking │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │ Relevant Job      │
                         │ Recommendations   │
                         └───────────────────┘
```

---

# 🧠 AI / Semantic Matching Architecture

The semantic matching pipeline works as follows:

```text
                JOB DATA
                   │
                   ▼
            Data Processing
                   │
                   ▼
              Job Text
                   │
                   ▼
         Embedding Generation
                   │
                   ▼
               Qdrant
                   │
                   │
User Query ────────┘
      │
      ▼
Query Embedding
      │
      ▼
Vector Similarity Search
      │
      ▼
Candidate Jobs
      │
      ▼
Matching / Ranking
      │
      ▼
Final Recommendations
```

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| Frontend Tooling | Vite |
| Programming Language | Python |
| Backend | FastAPI |
| API Server | Uvicorn |
| Relational Database | PostgreSQL |
| Vector Database | Qdrant |
| Data Validation | Pydantic |
| Database Access | SQLAlchemy |
| PDF Processing | pypdf |
| DOCX Processing | python-docx |
| File Uploads | python-multipart |
| Version Control | Git / GitHub |

---

# 📊 Dataset

The project uses a large job dataset stored at:

```text
data/raw/jobs.json
```

During development, the ingestion pipeline processed approximately:

```text
56,769 job records
```

After duplicate handling:

```text
45,579 jobs inserted
11,190 duplicates
0 errors
```

### Ingestion Result

```text
INGESTION COMPLETE

Processed:   56,769
Inserted:    45,579
Duplicates:  11,190
Errors:      0
```

---

# 📁 Project Structure

```text
Research Analyst project/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   ├── resume.py
│   │   │   └── ...
│   │   │
│   │   ├── services/
│   │   │   ├── resume_service.py
│   │   │   └── ...
│   │   │
│   │   ├── ...
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── RecommendationCard.jsx
│   │   │   └── ...
│   │   │
│   │   ├── pages/
│   │   │   ├── Jobs.jsx
│   │   │   ├── Assistant.jsx
│   │   │   ├── Recommendations.jsx
│   │   │   └── ...
│   │   │
│   │   └── ...
│   │
│   └── package.json
│
├── scripts/
│   ├── init_db.py
│   ├── ingest_jobs.py
│   ├── index_jobs.py
│   ├── generate_embeddings.py
│   ├── deduplicate_jobs.py
│   ├── enrich_jobs.py
│   ├── inspect_dataset.py
│   ├── verify_database.py
│   ├── reset_jobs.py
│   ├── test_ingestion.py
│   ├── test_retrieval.py
│   └── test_vector_store.py
│
├── data/
│   ├── raw/
│   │   └── jobs.json
│   ├── processed/
│   └── qdrant/
│
├── .env.example
├── .gitignore
└── README.md
```

---

# ⚙️ Installation & Setup

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd "Research Analyst project"
```

---

# 🐍 Backend Setup

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

Install backend dependencies:

```bash
pip install -r backend\requirements.txt
```

If individual dependencies are missing:

```bash
pip install pypdf
pip install python-docx
pip install python-multipart
```

---

# 🔐 Environment Variables

Create a local `.env` file based on `.env.example`.

Example structure:

```env
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE

QDRANT_URL=YOUR_QDRANT_URL
QDRANT_API_KEY=YOUR_QDRANT_API_KEY

GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
```

> ⚠️ **Never commit `.env` or real API keys/passwords to GitHub.**

Only `.env.example` should be committed.

---

# 🐘 PostgreSQL Setup

The application uses PostgreSQL to store structured job data.

Connection format:

```text
postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE
```

Make sure PostgreSQL is:

- Installed
- Running
- Configured with the required database
- Accessible using the credentials in `.env`

---

# 🗄️ Initialize the Database

From the project root:

```bash
python scripts\init_db.py
```

This initializes the required database tables.

---

# 📥 Ingest the Job Dataset

Run:

```bash
python scripts\ingest_jobs.py
```

The ingestion process:

1. Reads the raw JSON dataset
2. Processes job records
3. Validates records
4. Detects duplicates
5. Inserts valid jobs into PostgreSQL
6. Reports ingestion statistics

---

# 🔍 Verify the Database

Run:

```bash
python scripts\verify_database.py
```

This verifies that job records were successfully inserted into PostgreSQL.

---

# 🧰 Data Utility Scripts

### Inspect Dataset

```bash
python scripts\inspect_dataset.py
```

### Reset Jobs

```bash
python scripts\reset_jobs.py
```

### Deduplicate Jobs

```bash
python scripts\deduplicate_jobs.py
```

### Enrich Jobs

```bash
python scripts\enrich_jobs.py
```

### Generate Embeddings

```bash
python scripts\generate_embeddings.py
```

### Index Jobs

```bash
python scripts\index_jobs.py
```

---

# 🧠 Qdrant Setup

Qdrant is used as the vector database for semantic job retrieval.

The general pipeline is:

```text
Job Data
   ↓
Text Processing
   ↓
Embedding Generation
   ↓
Qdrant
   ↓
Vector Similarity Search
   ↓
Relevant Jobs
```

Configure the Qdrant connection using the environment variables in `.env`.

---

# ▶️ Start the Backend

Run the backend from the **project root**:

```bash
python -m uvicorn backend.app.main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

---

# 📚 API Documentation

FastAPI automatically provides interactive API documentation.

Once the backend is running, open:

```text
http://127.0.0.1:8000/docs
```

The Swagger UI allows you to:

- Explore API endpoints
- Test requests
- Upload resumes
- View request parameters
- View API responses

---

# 💻 Frontend Setup

Open a second terminal.

Move into the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🔄 Running the Complete Application

## Terminal 1 — Backend

```bash
cd "Research Analyst project"

venv\Scripts\activate

python -m uvicorn backend.app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

---

## Terminal 2 — Frontend

```bash
cd "Research Analyst project\frontend"

npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 🧪 Testing

The project includes scripts for testing different parts of the application.

### Test Ingestion

```bash
python scripts\test_ingestion.py
```

### Test Retrieval

```bash
python scripts\test_retrieval.py
```

### Test Vector Store

```bash
python scripts\test_vector_store.py
```

---

# 📄 Resume Processing

The Resume Match feature supports:

- PDF
- DOCX

### PDF Processing

PDF files are processed using:

```python
from pypdf import PdfReader
```

### DOCX Processing

DOCX files are processed using:

```python
from docx import Document
```

### File Upload

FastAPI file uploads require:

```text
python-multipart
```

Install it with:

```bash
pip install python-multipart
```

---

# 🎨 User Interface

The frontend was redesigned to maintain a consistent visual system across all major sections.

### Main Sections

| Section | Purpose |
|---|---|
| Jobs | Browse and search jobs |
| AI Assistant | Natural-language job search |
| Recommendations | Personalized job matching |
| Resume Match | Resume-based job recommendations |

### UI Design Principles

- Warm creamy background
- Clean white cards
- Mauve accent color
- Rounded components
- Subtle shadows
- Minimal borders
- Consistent spacing
- Responsive layouts
- Professional typography

---

# 📸 Screenshots

Add screenshots of the application here.

### Jobs

> Add Jobs page screenshot here.

### AI Job Assistant

> Add AI Assistant screenshot here.

### Recommendations

> Add Recommendations screenshot here.

### Resume Match

> Add Resume Match screenshot here.

---

# 🔐 Security

Sensitive information should never be committed to the repository.

Do **not** commit:

```text
.env
```

Do **not** expose:

```text
DATABASE_PASSWORD
QDRANT_API_KEY
GOOGLE_API_KEY
```

Use:

```text
.env
```

for local secrets.

Use:

```text
.env.example
```

for documenting required environment variables.

---

# 👥 Collaboration

The project can be developed collaboratively.

Each developer should maintain their own:

- `.env`
- PostgreSQL credentials
- API keys
- Python virtual environment
- Local configuration

The following should be shared through Git:

- Backend source code
- Frontend source code
- Scripts
- Configuration templates
- Documentation

The following should **not** be shared through Git:

- Passwords
- API keys
- `.env`
- Virtual environments
- Sensitive credentials

---

# 🔀 Git Workflow

Before starting development:

```bash
git pull origin main
```

Check the current status:

```bash
git status
```

Stage changes:

```bash
git add .
```

Commit changes:

```bash
git commit -m "your commit message"
```

Push changes:

```bash
git push origin main
```

### Example

```bash
git add .
git commit -m "feat: redesign frontend UI for consistent job matching experience"
git push origin main
```

---

# ⚠️ Common Issues

## `ModuleNotFoundError: No module named 'backend'`

Make sure you are running the command from the project root.

Use:

```bash
python -m uvicorn backend.app.main:app --reload
```

---

## `ModuleNotFoundError: No module named 'app'`

Do not run:

```bash
uvicorn app.main:app
```

from the project root.

Use:

```bash
python -m uvicorn backend.app.main:app --reload
```

---

## `ModuleNotFoundError: No module named 'pypdf'`

Run:

```bash
pip install pypdf
```

---

## `ModuleNotFoundError: No module named 'docx'`

Run:

```bash
pip install python-docx
```

The installation package is `python-docx`, while the Python import is:

```python
from docx import Document
```

---

## `Form data requires "python-multipart"`

Run:

```bash
pip install python-multipart
```

This dependency is required for FastAPI file uploads.

---

## PostgreSQL Connection Error

Check:

- PostgreSQL is running
- Database exists
- Username is correct
- Password is correct
- Host is correct
- Port is correct
- `DATABASE_URL` is configured correctly

---

## Database Contains Zero Jobs

Run:

```bash
python scripts\verify_database.py
```

If the database contains zero jobs, run:

```bash
python scripts\ingest_jobs.py
```

Then verify again:

```bash
python scripts\verify_database.py
```

---

# 🔄 Fresh Project Setup

For a completely fresh setup:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>

cd "Research Analyst project"

python -m venv venv

venv\Scripts\activate

pip install -r backend\requirements.txt
```

Configure your `.env`.

Initialize the database:

```bash
python scripts\init_db.py
```

Load the dataset:

```bash
python scripts\ingest_jobs.py
```

Verify the database:

```bash
python scripts\verify_database.py
```

Start the backend:

```bash
python -m uvicorn backend.app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

In another terminal:

```bash
cd frontend

npm install

npm run dev
```

Open:

```text
http://localhost:5173
```

---

# 📈 Project Status

## Backend

- [x] FastAPI backend
- [x] PostgreSQL integration
- [x] Database initialization
- [x] Job ingestion
- [x] Duplicate handling
- [x] Database verification
- [x] Resume upload
- [x] PDF processing
- [x] DOCX processing
- [x] Recommendation APIs
- [x] Semantic search infrastructure

## Frontend

- [x] Jobs page
- [x] AI Job Assistant
- [x] Recommendations page
- [x] Resume Match
- [x] Recommendation cards
- [x] Consistent UI design
- [x] Responsive styling

## Data & Retrieval

- [x] Raw job dataset
- [x] PostgreSQL job storage
- [x] Duplicate handling
- [x] Embedding pipeline
- [x] Qdrant vector search infrastructure

---

# 🎯 Project Goals

The main goals of the platform are:

- Make job discovery easier
- Reduce dependence on keyword-based search
- Understand natural-language job requirements
- Provide semantic job matching
- Generate personalized job recommendations
- Match resumes with relevant opportunities
- Rank jobs according to relevance
- Provide a clean and professional user experience
- Build a scalable AI-powered job research platform

---

# 🚀 Future Improvements

Potential future enhancements include:

- Advanced job filtering
- Improved recommendation ranking
- User profiles
- Saved jobs
- Job application tracking
- Authentication and authorization
- More advanced resume analysis
- Explainable recommendation scores
- Improved semantic retrieval
- Production deployment
- Automated job-data updates
- Analytics dashboard

---

# 👥 Contributors

### Deepthi

AI / Data / Full-Stack Development

### Project Collaborator

Backend / Frontend / AI Development

---

# 📄 License

This project is currently intended for educational, portfolio, and development purposes.