# 🔧 Backend - Agentic RAG System

FastAPI-based backend implementing a 5-agent pipeline for financial report analysis with intelligent retry mechanisms, JSON repair fallbacks, and persistent vector storage.

## 🏗️ Architecture

### Agent Pipeline

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  1. PLANNER AGENT                                       │
│  • Analyzes query intent (ratio/trend/risk/summary)    │
│  • Identifies required metrics                         │
│  • Determines time range                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. RETRIEVER AGENT                                     │
│  • Semantic search in ChromaDB                         │
│  • Ranks chunks by relevance                           │
│  • Adjusts depth on retries (5 → 7 → 9 chunks)        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  3. ANALYZER AGENT                                      │
│  • Extracts financial metrics from context             │
│  • Performs calculations (margins, ratios, growth)     │
│  • Structures data for generator                       │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  4. GENERATOR AGENT                                     │
│  • Creates structured JSON response                    │
│  • JSON repair fallback via SOP                        │
│  • Includes exec summary, analysis, risks, metrics     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  5. CRITIC AGENT                                        │
│  • Validates response quality                          │
│  • Computes confidence score (0.0-1.0)                 │
│  • Triggers retry if confidence < 0.7                  │
│  • Applies exponential weight decay                    │
└─────────────────────────────────────────────────────────┘
    │                                    │
    ▼ (confidence >= 0.7)                ▼ (confidence < 0.7)
Return Response                    Retry with adjusted params
```

## 📁 Project Structure

```
backend/
├── agents/
│   ├── __init__.py
│   ├── planner.py          # Query intent classification
│   ├── retriever.py        # Semantic document retrieval
│   ├── analyzer.py         # Financial metric extraction
│   ├── generator.py        # Response generation with SOP
│   └── critic.py           # Quality validation & retry logic
│
├── db/
│   ├── __init__.py
│   └── chroma_client.py    # ChromaDB wrapper & persistence
│
├── ingestion/
│   ├── __init__.py
│   ├── pdf_parser.py       # PDF text extraction + OCR
│   └── chunking.py         # Semantic chunking with overlap
│
├── utils/
│   ├── __init__.py
│   ├── ollama_client.py    # LLM API client + JSON repair
│   └── weight_decay.py     # Retry parameter adjustment
│
├── config.py               # Configuration & environment
├── main.py                 # FastAPI application
└── requirements.txt        # Python dependencies
```

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Install Ollama (if not already installed)

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai

# Pull model
ollama pull llama3.1:8b
```

### 3. Optional: Install Tesseract OCR

For scanned PDFs with images:

```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

### 4. Configure Environment

Create `.env` file or edit `config.py`:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# LLM Parameters
LLM_TEMPERATURE=0.1         # Lower = more deterministic
LLM_MAX_TOKENS=2000         # Max response length

# Retrieval Settings
TOP_K_CHUNKS=5              # Initial chunks to retrieve
CHUNK_SIZE=500              # Characters per chunk
CHUNK_OVERLAP=50            # Overlap between chunks

# Quality Control
CONFIDENCE_THRESHOLD=0.7    # Retry if below this
MAX_RETRIES=3               # Maximum retry attempts

# Storage
CHROMA_PERSIST_DIR=../chroma_db
UPLOADS_DIR=../uploads
```

### 5. Run Server

```bash
python main.py
```

Server will start on `http://localhost:8888`

## 📡 API Endpoints

### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "documents_indexed": 22,
  "ollama_url": "http://localhost:11434",
  "model": "llama3.1:8b"
}
```

### Upload PDF
```bash
POST /upload
Content-Type: multipart/form-data

Body: file=@document.pdf

Response:
{
  "message": "PDF processed successfully",
  "filename": "document.pdf",
  "chunks_created": 11,
  "status": "success"
}
```

### Query Documents
```bash
POST /query
Content-Type: application/json

Body:
{
  "question": "What is the net profit margin?"
}

Response:
{
  "query": "What is the net profit margin?",
  "plan": {
    "intent": "ratio_analysis",
    "metrics_required": ["net profit margin"],
    "time_range": null
  },
  "executive_summary": "...",
  "analysis": {...},
  "risk_factors": "...",
  "confidence": 0.85,
  "retry_count": 0,
  "final_weight": 1.0
}
```

### Get Statistics
```bash
GET /stats

Response:
{
  "total_documents": 2,
  "total_chunks": 22,
  "queries_processed": 19,
  "avg_response_time": 4.23
}
```

### Query History
```bash
GET /history

Response:
{
  "history": [...],
  "count": 19
}
```

## 🧠 Agent Details

### 1. Planner Agent (`agents/planner.py`)

**Purpose:** Analyze user query and determine analysis strategy

**Outputs:**
- `intent`: ratio_analysis | trend_analysis | risk_analysis | summarization
- `metrics_required`: List of financial metrics needed
- `time_range`: Date range for analysis (if applicable)

**Example:**
```python
plan = create_plan("What is the debt-to-equity ratio?")
# Returns: {'intent': 'ratio_analysis', 'metrics_required': ['debt-to-equity ratio'], ...}
```

### 2. Retriever Agent (`agents/retriever.py`)

**Purpose:** Retrieve relevant document chunks via semantic search

**Features:**
- Semantic similarity search using embeddings
- Configurable top-k retrieval
- Adaptive depth on retries (5 → 7 → 9 chunks)
- Metadata filtering support

**Example:**
```python
chunks, context = retrieve_context(query="net profit margin", top_k=5)
# Returns: (chunk_objects, concatenated_text)
```

### 3. Analyzer Agent (`agents/analyzer.py`)

**Purpose:** Extract and compute financial metrics from context

**Capabilities:**
- Ratio calculations (profit margin, ROE, debt ratios)
- Growth rate computations (YoY, CAGR)
- Trend identification
- Data validation

**Example:**
```python
metrics = analyze_context(context, intent="ratio_analysis")
# Returns: {'net_profit_margin_percent': 15.5, ...}
```

### 4. Generator Agent (`agents/generator.py`)

**Purpose:** Generate structured natural language responses

**Features:**
- Structured JSON output (exec summary, analysis, risks)
- JSON repair fallback using SOP (Structured Output Parser)
- Confidence-based quality estimation
- Temperature-adjustable generation

**JSON Repair Process:**
1. Initial LLM generation attempt
2. If JSON parse fails → Sanitize (remove comments, trailing commas)
3. If still fails → Send to LLM for strict JSON correction
4. Return repaired JSON or fallback defaults

**Example:**
```python
response = generate_response(
    query="What is the margin?",
    context=retrieved_context,
    intent="ratio_analysis",
    computed_metrics={'margin': 15.5}
)
```

### 5. Critic Agent (`agents/critic.py`)

**Purpose:** Validate response quality and trigger retries

**Validation Criteria:**
- Information completeness
- Numerical accuracy
- Source reliability
- Coherence and clarity

**Confidence Scoring:**
- `0.9-1.0`: Excellent - all info available, high certainty
- `0.7-0.9`: Good - most info available, minor gaps
- `0.5-0.7`: Fair - significant gaps, retry recommended
- `0.0-0.5`: Poor - insufficient info, definite retry

**Retry Logic:**
- Retry if confidence < 0.7 (MAX_RETRIES=3)
- Adjusts temperature: `base * (1 + 0.2 * retry_count)`
- Increases retrieval depth: `base_k + 2 * retry_count`
- Applies exponential weight decay to confidence

**Example:**
```python
evaluation = evaluate_response(response, query, retry_count=0)
# Returns: {'confidence': 0.75, 'should_retry': False, 'weight': 1.0, ...}
```

## 🔄 Retry Mechanism

### Weight Decay Formula

```python
weight = math.exp(-0.5 * retry_count)

# Retry 0: weight = 1.0
# Retry 1: weight = 0.606
# Retry 2: weight = 0.368
# Retry 3: weight = 0.223
```

### Parameter Adjustment on Retry

| Parameter | Initial | Retry 1 | Retry 2 | Retry 3 |
|-----------|---------|---------|---------|---------|
| Temperature | 0.1 | 0.12 | 0.14 | 0.16 |
| Retrieval Depth | 5 | 7 | 9 | 11 |
| Confidence Weight | 1.0 | 0.61 | 0.37 | 0.22 |

## 🗄️ Database Layer

### ChromaDB Integration (`db/chroma_client.py`)

**Features:**
- Persistent vector storage on disk
- Automatic embedding generation via Ollama
- Metadata filtering (source, page, chunk_id)
- Collection management (create, delete, reset)

**Key Methods:**
```python
chroma = get_chroma_client()

# Add documents
chroma.add_documents(chunks)

# Search
results = chroma.search(query, top_k=5)

# Count
total = chroma.count_documents()

# Delete collection
chroma.delete_collection()
```

## 📄 PDF Processing (`ingestion/`)

### PDF Parser (`pdf_parser.py`)

**Extraction Pipeline:**
1. Try text extraction with pypdf
2. If text < 100 chars → OCR fallback with Tesseract
3. Clean and normalize text
4. Return list of page dictionaries

**Example:**
```python
pages = extract_pdf("financial_report.pdf")
# Returns: [{'page_num': 1, 'text': '...'}, ...]
```

### Chunking (`chunking.py`)

**Strategy:**
- Fixed size chunks with overlap
- Preserves sentence boundaries where possible
- Includes metadata (source, page, chunk_id)

**Example:**
```python
chunks = chunk_document(pages, filename="report.pdf")
# Returns: [{'text': '...', 'metadata': {...}}, ...]
```

## 🛠️ Utilities

### Ollama Client (`utils/ollama_client.py`)

**Features:**
- Text generation with temperature control
- JSON generation with automatic repair
- Embedding generation for semantic search
- Timeout handling and error recovery

**JSON Repair Fallback:**
```python
# Attempt 1: Parse JSON directly
# Attempt 2: Sanitize and parse (remove comments, trailing commas)
# Attempt 3: Ask LLM to repair with strict JSON rules
```

### Weight Decay (`utils/weight_decay.py`)

**Functions:**
- `compute_adjusted_temperature(base, retry)` - Increases temperature
- `compute_retrieval_depth(base, retry)` - Increases chunk count
- `compute_weight(retry)` - Exponential decay

## 🧪 Testing

### Run Unit Tests
```bash
python test_api.py
```

### Run Integration Tests
```bash
python test_comprehensive.py
```

**Test Coverage:**
- PDF upload and processing
- Agent pipeline execution
- Retry mechanism
- JSON repair fallback
- Statistics calculation
- Query history

## 🔍 Debugging

### Enable Debug Logging
```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### View Ollama Logs
```bash
# Check Ollama service logs
journalctl -u ollama  # Linux
```

### Inspect ChromaDB
```python
from db import get_chroma_client

chroma = get_chroma_client()
print(f"Documents: {chroma.count_documents()}")
print(f"Collections: {chroma.collection.name}")
```

## ⚙️ Performance Tuning

### Reduce Response Time
1. Lower `TOP_K_CHUNKS` (5 → 3)
2. Reduce `LLM_MAX_TOKENS` (2000 → 1500)
3. Increase `CONFIDENCE_THRESHOLD` (0.7 → 0.6) to avoid unnecessary retries
4. Use smaller model: `llama3:7b` instead of `llama3.1:8b`

### Improve Accuracy
1. Increase `TOP_K_CHUNKS` (5 → 7)
2. Lower `LLM_TEMPERATURE` (0.1 → 0.05)
3. Reduce `CHUNK_SIZE` (500 → 400) for finer granularity
4. Increase `CHUNK_OVERLAP` (50 → 100)

## 🚨 Common Issues

### Issue: "Connection refused to Ollama"
```bash
# Start Ollama service
ollama serve
```

### Issue: "Model not found"
```bash
# Pull the model
ollama pull llama3.1:8b
```

### Issue: "ChromaDB locked"
```bash
# Close all other processes using the DB, or:
rm -rf chroma_db
# Database will be recreated
```

### Issue: "OCR not working"
```bash
# Install Tesseract
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Guide](https://docs.trychroma.com/)
- [Ollama API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Pydantic Models](https://docs.pydantic.dev/)

---

**For frontend documentation, see [`../frontend/README.md`](../frontend/README.md)**
