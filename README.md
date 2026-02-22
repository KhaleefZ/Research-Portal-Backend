

# 📊 Financial Research Portal - Backend

This is the AI-powered backend for the **Financial Research Portal (Option A)**. It specializes in extracting, standardizing, and exporting consolidated financial metrics from complex, multi-page PDF quarterly reports using **FastAPI** and **Gemini 1.5 Flash**.

## 🚀 Live Demo & API

* **Live API URL**: `https://your-backend-link.onrender.com`
* **Swagger Documentation**: `https://your-backend-link.onrender.com/docs`

---

## 🛠️ Tech Stack

* **Framework**: FastAPI (Python 3.10+)
* **AI Model**: Google Gemini 1.5 Flash (via `google-genai`)
* **PDF Engine**: PyMuPDF (`fitz`) for high-speed text extraction
* **Data Processing**: Pandas & OpenPyXL
* **Export Engine**: XlsxWriter (for professional Excel formatting)
* **Deployment**: Render

---

## 📂 System Architecture

The backend follows a modular **Service-Oriented Architecture** to ensure clean code and reliability:

1. **Ingestion Layer**: Validates file types and reads raw bytes from the multipart upload.
2. **Processing Layer (`pdf_processor.py`)**: Converts PDF pages into structured text blocks while preserving table alignments.
3. **Extraction Engine (`research_tool.py`)**: A hybrid system that uses regex for common patterns and Gemini 1.5 Flash for complex "Judgment Calls" (e.g., distinguishing between Standalone and Consolidated data).
4. **Formatting Layer (`excel_exporter.py`)**: Transforms JSON data into a pivot-table style Excel sheet with professional branding.

---

## 🧪 Key Features for Analysts

* **Smart Metric Mapping**: Automatically maps various naming conventions (e.g., "Revenue from Operations" vs. "Total Sales") into a standardized "Total Revenue" field.
* **Multi-Period Support**: Intelligently handles tables containing multiple columns (Quarter Ended vs. Year Ended) as seen in **Tata Motors** reports.
* **Error Resilience**: Includes health check endpoints (`/`) and robust error handling for API rate limits (429) or service spikes (503).
* **Streaming Downloads**: Uses `StreamingResponse` to deliver Excel files efficiently without overwhelming server memory.

---

## 📥 Installation & Local Setup

1. **Clone the repository**:
```bash
git clone https://github.com/your-username/research-tool.git
cd research-tool/backend

```


2. **Set up Virtual Environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```


3. **Install Dependencies**:
```bash
pip install -r requirements.txt

```


4. **Environment Variables**:
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_google_ai_studio_key
PORT=8000

```


5. **Run the Server**:
```bash
uvicorn app.main:app --reload

```



---

## 📡 API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Health check & service status. |
| `POST` | `/api/research/extract-financials` | Upload PDF and receive a formatted Excel file. |

---

## 📋 Evaluator Note

This tool was specifically tested against:

* **Dabur India Ltd (Q3 FY25)**: Targets the "Consolidated" table on Page 5.
* **Tata Motors (March 2025)**: Targets the primary "Audited Financial Results" on Page 1.

**Would you like me to also provide a similarly structured README for the React Frontend?**
