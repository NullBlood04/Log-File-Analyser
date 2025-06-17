# 📋 Windows Event Log Analyzer

A Streamlit-based application that automates the process of extracting Windows Error Event Logs, filters out duplicates, and provides intelligent analysis using Azure OpenAI (via LangChain).

---

## 🚀 Features

- 📤 **Extracts Windows Application Error Logs** using a PowerShell script  
- 🧹 **Filters duplicate logs** to avoid repetition and reduce noise  
- 🤖 **Analyzes log messages** using GPT (via Azure OpenAI and LangChain)  
- 💡 **Explains errors in simple terms** with step-by-step resolution suggestions  
- 🧾 **Displays logs in a web interface** using Streamlit

---

## 🏗️ Project Structure

```
.
├── CSVfiles/
│   ├── AppErrorLogs.csv       # Raw event logs
│   └── UniqueErrors.csv       # Deduplicated logs
├── ProgramFiles/
    └── powershell/
        └── log_export_csv.ps1 # PowerShell script for log extraction
    └── python
        ├── AI_handler.py              # Azure OpenAI wrapper via LangChain
        ├── Log_to_Csv.py              # PowerShell subprocess trigger
        ├── represent_csv.py           # CSV loading and display logic
        ├── filter_unique_field.py     # Removes duplicate logs based on EventID
        └── main.py                    # Main entry point (contains StreamlitRendering)
├── .env                       # Environment variables for Azure OpenAI
└── README.md                  # You're here!
```

---

## 🛠️ Requirements

- Python 3.9+
- PowerShell (Windows only)
- [Azure OpenAI resource](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/overview)
- `AppErrorLogs.csv` generated via PowerShell
- `.env` file configured (see below)

---

## 🔐 `.env` File Format

```
AZURE_OPENAI_API_KEY=your-api-key
AZURE_DEPLOYMENT_NAME=your-deployment-name
AZURE_RESOURCE_NAME=your-resource-name
AZURE_API_VERSION=2024-02-15-preview
```

---

## 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

**`requirements.txt` example:**
```text
streamlit
langchain
langchain-openai
python-dotenv
pandas
```

---

## ▶️ Run the App

```bash
streamlit run main.py
```

---

## ⚙️ How It Works

1. **Log Extraction**  
   A PowerShell script (`log_export_csv.ps1`) extracts Application Error logs for a given source.

2. **Duplicate Removal**  
   The script filters logs based on unique `EventID` and writes only unseen entries to `UniqueErrors.csv`.

3. **Log Analysis**  
   Each error can be submitted to Azure OpenAI for analysis via a button in the UI.

4. **UI Display**  
   Streamlit shows a searchable, interactive log table and response area.

---

## 📸 Screenshot (Optional)

You can include a screenshot of the Streamlit UI here if you'd like.

---

## 🧠 AI Behavior

The AI is prompted with a clear system instruction to analyze logs, explain the error, and provide solutions in a concise and user-friendly tone. It responds with practical advice that helps users understand and act on the error messages.

---

## ✅ Future Improvements

- [ ] Add filtering by date, severity, or source  
- [ ] Enable multi-log comparison  
- [ ] Support other log types (e.g., System, Security)  
- [ ] Archive old logs for long-term analysis  
- [ ] Deploy on an internal network or intranet

---

## 📄 License

This project is for internal use and educational purposes. For external/public deployment, ensure compliance with Microsoft and OpenAI usage policies.