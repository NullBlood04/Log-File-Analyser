# 📋 Windows Event Log Analyzer

A Flask-based application that automates the process of extracting Windows Error Event Logs, filters out duplicates, and provides intelligent analysis using Azure OpenAI (via LangChain).

---

## 🚀 Features

-   💬 **Chatbot Interface:** Interact with the log analyzer through a conversational chatbot.
-   📤 **Extracts Windows Application Error Logs** using a PowerShell script ([`extract_logs.ps1`](ProgramFiles/powershell/extract_logs.ps1)).
-   🤖 **Analyzes log messages** using GPT (via Azure OpenAI and LangChain).
-   💡 **Explains errors in simple terms** with step-by-step resolution suggestions.
-   🗄️ **Database Storage:** Stores extracted logs in a MySQL database.
-   🔍 **Error Frequency Analysis:** Determines the frequency of errors using AI.
-   💻 **System Probing:** Executes validated PowerShell scripts to gather system information.

---

## 🏗️ Project Structure

```
.
├── ProgramFiles/
│   ├── powershell/
│   │   └── extract_logs.ps1          # PowerShell script to extract logs from Windows Event Logs
│   └── python/
│       ├── dependency/
|       |   ├── __init__.py               # Package initializer, may import and trigger database creation
│       │   ├── Agents/
│       │   │   ├── chatbot.py        # Contains chatbot logic and LangGraph implementation
│       │   │   ├── frequencyAgent.py # Agent for analyzing error frequency
│       │   │   └── resultAgent.py    # Agent for analyzing error content and suggesting solutions
│       │   |
│       |   ├── AdditionalTools/
|       |       ├── parent_aiConnector.py # Wrapper to connect to Azure OpenAI APIs
│       │       ├── chatbotTools.py       # Tools used by the chatbot: database operations, frequency analysis, result analysis, system probing
│       │       ├── createDatabase.py     # Script to create and populate the MySQL database
│       │       ├── literals.py           # Large string literals like prompts and templates
│       │       └── sqlConnection.py      # Class for MySQL database connection handling
│       |
│       └── main.py                   # Flask app entry point to run the web interface
├── static/
│   ├── scripts.js                    # JavaScript for client-side chat interface interactivity
│   └── styles.css                    # CSS styling for the web interface
├── templates/
│   └── chat.html                     # HTML template for the chat web page (Flask renders this)
├── TextFiles/
│   └── last_recordedId.txt           # Stores last recorded event ID to avoid duplicate log processing
├── .env                              # Environment variables (Azure OpenAI keys, database credentials, etc.)
└── README.md                         # You're Here

```

---

## 🛠️ Requirements

-   Python 3.9+
-   PowerShell (Windows only)
-   [Azure OpenAI resource](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/overview)
-   MySQL Database
-   `.env` file configured (see below)

---

## 🔐 `.env` File Format
```text
AZURE_OPENAI_API_KEY=your-api-key
AZURE_DEPLOYMENT_NAME=your-deployment-name
AZURE_RESOURCE_NAME=your-resource-name
AZURE_API_VERSION=2024-02-15-preview
MYSQL_USER=your-mysql-username
MYSQL_PASSWORD=your-mysql-password
```

---

## 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

**`requirements.txt` example:**
```text
Flask
markdown2
langchain
langgraph
langchain-openai
python-dotenv
mysql-connector-python
typing_extensions
re
os
```

---

## ▶️ Run the App

   1. **Set up the database**
      - Ensure **MySQL** is installed and running.
      - Create a database named `log`.
      - The `create_errorDbase()` function in `createDatabase.py` will create the `application_errors` table if it doesn't exist.

   2. **Run the Flask app**
      ```ps1
      python ProgramFiles/python/main.py
      ```

   3. **Open in your browser:**
      - Open your browser and navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## ⚙️ How It Works

   1. **Log Extraction**

      - The createDatabase.create_errorDbase function uses a PowerShell script (extract_logs.ps1) to extract Application Error logs.
      - The script retrieves logs with Error or Critical level and a RecordId greater than the last recorded ID (stored in TextFiles/last_recordedId.txt).
      - The extracted logs are converted to JSON format.

   2. **Database Storage**

      - The extracted logs are stored in the application_errors table in the MySQL database.
      - The createDatabase.create_errorDbase function connects to the database using the credentials from the .env file.
      - The last_recordedId is updated in last_recordedId.txt to prevent duplicate entries.
   
   3. **Chatbot Interface**

      - The Flask application serves a chat interface using the chat.html template and the associated static files (scripts.js and static/styles.css).
      - User input is sent to the /chat endpoint, which uses the ChatBot class to process the input.

   4. **AI-Powered Analysis**

      - The ChatBot class uses LangGraph to orchestrate different agents and tools.
      - The available tools are defined in chatbotTools.py and include:
         + database_tool: For executing SQL queries against the database.
         + errorFrequencyAgent_prompt_node: For summarizing the frequency of errors based on timestamps.
         + resultAgent_prompt_node: For analyzing error content and providing explanations and solutions.
         + probe_system: For executing validated PowerShell scripts.
      - The agents use Azure OpenAI to generate responses based on the provided prompts (defined in literals.py).

---

## 🧠 AI Behavior

The AI is prompted with **clear system instructions** to analyze logs, explain errors, and provide solutions in a concise and user-friendly tone. It responds with practical advice to help users understand and act on error messages.

Key agents:

- **ResultAgent**: Detailed error analysis and solutions.
- **ErrorFrequencyAgent**: Summarizes error occurrence patterns.

---

## ✅ Future Improvements

- [ ] Implement user authentication and authorization.
- [ ] Add filtering by date, severity, or source.
- [ ] Enable multi-log comparison.
- [ ] Support other log types (e.g., System, Security).
- [ ] Archive old logs for long-term analysis.
- [ ] Deploy on an internal network or intranet.

---

## 📄 License

This project is for **internal use and educational purposes**. For external or public deployment, ensure compliance with **Microsoft** and **OpenAI usage policies**.
