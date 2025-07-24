#  Windows Event Log Analyzer

An intelligent log analysis tool that uses LangChain and a dual-database system (MySQL + ChromaDB) to provide conversational insights into Windows Event Logs.

---

##  Features

-   **Conversational Interface:** Interact with your logs through an intuitive chatbot powered by LangGraph.
-   **Automated Log Ingestion:** A PowerShell script automatically extracts new Windows Application error logs.
-   **Incremental Processing:** Remembers the last log processed to prevent duplicate entries.
-   **Dual Database Storage:**
    -   **MySQL:** Stores structured log data for precise, query-based lookups.
    -   **ChromaDB:** Stores vector embeddings of log messages for powerful semantic search.
-   **Intelligent AI Analysis:** Leverages LLMs to analyze error frequency, explain complex error messages, and suggest solutions.
-   **Live System Probing:** Can run validated PowerShell commands to fetch real-time system information.

---

##  How It Works

The application operates in a clear, multi-stage process to turn raw event logs into actionable insights.

1.  **Log Ingestion (`process_logs.py`):**
    -   A background script executes a PowerShell command to fetch new Windows Application error logs since the last run, identified by a bookmark (`last_recordedId.txt`).
    -   The raw logs are parsed from JSON into a structured format.

2.  **Data Persistence (Dual DB):**
    -   **SQL (MySQL):** Structured data like `RecordId`, `EventID`, `Source`, and `TimeCreated` is inserted into the `application_errors` table. This is ideal for exact lookups (e.g., "Get error with RecordId 12345").
    -   **Vector (ChromaDB):** A descriptive sentence for each log is generated and stored as a vector embedding. This enables semantic search (e.g., "Find errors related to network failures").

3.  **User Interaction (Flask App):**
    -   The user interacts with a web-based chatbot served by a Flask application.

4.  **AI Orchestration (LangGraph):**
    -   User queries are routed by a central LangGraph agent which decides the best tool for the job.

5.  **Tool Execution:**
    -   **`query_sql_database`:** Used for specific, filtered queries against the MySQL database.
    -   **`query_chroma`:** Used for broad, semantic, or similarity-based searches against the ChromaDB vector store.
    -   **`probe_system`:** Used to execute safe, whitelisted PowerShell commands to get live system data.

6.  **Response Generation:**
    -   The results from the tools are synthesized by the LLM into a coherent, human-readable answer.

---

## 🏗️ Project Structure

```
.
├── ProgramFiles/
│   ├── powershell/
│   │   └── extract_logs.ps1      # PowerShell script to extract logs from Windows Event Viewer.
│   └── python/
│       ├── dependency/
│       │   ├── __init__.py
│       │   ├── Agents/
│       │   │   ├── chatbot.py        # Main LangGraph agent orchestrator.
│       │   │   └── ...               # Other specialized agents.
│       │   │
│       │   ├── AdditionalTools/
│       │   │   ├── tools/
│       │   │   │   ├── queryDBase.py     # Tool for querying the structured MySQL database.
│       │   │   │   ├── queryChroma.py    # Tool for semantic search in the ChromaDB vector store.
│       │   │   │   ├── frequencyTool.py  # Tool for finding frequency using timestamps.
│       │   │   │   ├── result.py         # Tool for analysing event and providing solution.
│       │   │   │   └── probeSystem.py    # Tool for executing safe system commands.
│       │   │   │
│       │   │   ├── sqlConnection.py  # Reusable class for MySQL database connections.
│       │   │   └── ...
│       │   │
│       │   └── initialSetups/
│       │       ├── createDatabase.py # One-time script to create the MySQL database and table.
│       │       └── process_logs.py   # Script to ingest logs into both MySQL and ChromaDB.
│       │
│       └── main.py                   # Flask app entry point to run the web interface.
│
├── static/                         # CSS and JS for the web interface.
├── templates/
│   └── chat.html                     # HTML template for the chatbot UI.
├── TextFiles/
│   └── last_recordedId.txt           # Stores the last processed RecordId to avoid duplicates.
├── .env                              # Environment variables (API keys, DB credentials).
├── chromaDB/                         # Directory for the persistent ChromaDB vector store.
└── README.md                         # You're here!
```

---

## 🛠️ Setup and Installation

### Prerequisites
-   Python 3.9+
-   PowerShell (for running on Windows)
-   An active MySQL server instance
-   An Azure OpenAI resource

### 1. Configure Environment Variables

Create a `.env` file in the project root and populate it with your credentials:

```text
AZURE_OPENAI_API_KEY="your-api-key"
RECORD_PATH="insert recordedId.txt from TextFiles"
AZURE_DEPLOYMENT_NAME="your-deployment-name"
AZURE_RESOURCE_NAME="your-resource-name"
AZURE_API_VERSION="2024-02-15-preview"
MYSQL_USER="your-mysql-username"
MYSQL_PASSWORD="your-mysql-password"
```

### 2. Install Dependencies

Install the required Python packages from your `requirements.txt` file.

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:
```text
Flask
langchain
langgraph
langchain-openai
python-dotenv
mysql-connector-python
chromadb
markdown2
typing_extensions
```

---

## ▶️ How to Run

Start the Flask server to launch the chatbot interface.
It automaticaly creates databases using `createDatabase.py` and populates it using `process_logs.py`


```bash
python ProgramFiles/python/main.py
```

Navigate to **`http://127.0.0.1:5000`** in your web browser to start chatting with your logs.

---

## ✅ Future Improvements

-   [ ] Implement user authentication and authorization.
-   [ ] Add UI controls for filtering logs by date, severity, or source.
-   [ ] Support other log types (e.g., System, Security).
-   [ ] Create a background service to run `process_logs.py` automatically.
-   [ ] Archive old logs to optimize performance.

---

## 📄 License

This project is intended for internal use and educational purposes. If you plan to deploy it publicly, ensure you comply with the usage policies of Microsoft Azure and OpenAI.