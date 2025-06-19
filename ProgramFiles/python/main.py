import streamlit as st
from represent_csv import LoadCSV
from AI_handler import Connect_AI
from Log_to_Csv import EventlogtoCSV
from filter_unique_field import GenerateUniqueField

class Main:


    def __init__(self) -> None:
        self.connect = Connect_AI()
        self.load_csv = LoadCSV()


    def button_click(self, dictionary, index):
        prompt_string = f"""
Event ID : {dictionary["EventID"][index]}
Source : {dictionary["Source"][index]}
Entry Type : {dictionary["EntryType"][index]}
Message : {dictionary["Message"][index]}
"""
        result = self.connect.prompt(prompt_string)
        st.markdown(f'<div class="result-content">{result}</div>', unsafe_allow_html=True)


    def generate_unique_csv(self, option) -> str:
        error_log_file = f"CSVfiles\\{option}\\{option}.csv"
        unique_log_file = f"CSVfiles\\{option}\\unique_{option}.csv"
        unique = GenerateUniqueField()
        unique.gen_unique(error_log_file, unique_log_file)
        return unique_log_file


    def streamlit_gui(self) -> None:
        convert_to_csv = EventlogtoCSV()
        st.set_page_config(page_title="Event Log Analyser", layout="wide")
        application_list = [
            ".NET Runtime",
            ".NET Runtime Optimization Service",
            "Application Error",
            "Application Hang",
            "brave",
            "Brave-Browser",
            "bravem",
            "CertEnroll",
            "Edge",
            "edgeupdate",
            "ESENT",
            "EventSystem",
            "igcc",
            "IntelDalJhi",
            "Microsoft-Windows-AppModel-State",
            "Microsoft-Windows-AppXDeploymentServer/Operational",
            "Microsoft-Windows-CAPI2",
            "Microsoft-Windows-Defrag",
            "Microsoft-Windows-Perflib",
            "Microsoft-Windows-RestartManager",
            "Microsoft-Windows-User Profiles Service",
            "Microsoft-Windows-WMI",
            "MSI Service",
            "MsiInstaller",
            "NortonSecurity",
            "NVIDIA app SelfUpdate Source",
            "OneDriveUpdaterService",
            "ProtonVPNService",
            "RtkAudioUniversalService",
            "SecurityCenter",
            "Service1",
            "Software Protection Platform Service",
            "VSS",
            "Windows Error Reporting",
            "Windows Search Service",
            "Wlclntfy",
            "WMIRegistrationService"
            ]
        

        st.markdown("""
    <style>
        .title {
            text-align: center;
            font-size: 3em;
            font-weight: bold;
            color: #00BFFF;
            margin-bottom: 1em;
        }
        .card {
            background-color: #1E1E1E;
            padding: 1.5em;
            height: 10em;
            border-radius: 15px;
            box-shadow: 0 0 20px rgba(0,0,0,0.3);
            border: 1px solid #2C2C2C;
            transition: all 0.3s ease-in-out;
        }
        
        .result-content {
            width: 360px;
            height: 390px;
            padding: 1em;
            overflow-y: auto;
            background-color: #1E1E1E;
            color: #cccccc;
            border-radius: 10px;
            border: 1px solid #333;
        }
                    
        .card:hover {
            transform: scale(1.02);
            box-shadow: 0 0 25px rgba(0, 191, 255, 0.2);
        }
        .card-title {
            font-size: 1.5em;
            font-weight: 600;
            color: #00BFFF;
            margin-bottom: 0.5em;
        }
        .card-body {
            font-size: 1em;
            color: #CCCCCC;
            margin-bottom: 1em;
            width: inherit;
            height: 6em;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .stButton>button {
            width: 100%;
            background-color: #00BFFF;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6em 1em;
            font-size: 0.95em;
            transition: 0.2s ease;
            margin-top: -1em;
        }
        .stButton>button:hover {
            background-color: #009ACD;
        }
    </style>
""", unsafe_allow_html=True)
        
        st.markdown('<div class="title">Event Log Analyser</div>', unsafe_allow_html=True)

        option = st.selectbox("Select application", application_list)
        convert_to_csv.extract_evt_files(option)
        unique_log_file = self.generate_unique_csv(option)

        self.load_csv.extract_from(unique_log_file)

        st.dataframe(self.load_csv.display_csv())
        csv_dict = self.load_csv.display_csv_dict()

        timegendict = csv_dict["TimeGenerated"]
        for i in range(0, len(timegendict), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if (i + j) < len(timegendict):
                    with col:
                        st.markdown(f"""
                            <div class="card">
                                <div class="card-title">EventID: {csv_dict['EventID'][i+j]}</div>
                                <div class="card-body">{csv_dict['Message'][i+j]}</div>
                            </div>
                        """, unsafe_allow_html=True)

                        if st.button("Analyse", key=(i+j)):
                            self.button_click(csv_dict, (i+j))


if __name__ == "__main__":
    main = Main()
    main.streamlit_gui()
