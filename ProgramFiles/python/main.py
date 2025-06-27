import streamlit as st
from represent_csv import LoadCSV
from AI_handler import ResultAgent
from Log_to_Csv import EventlogtoCSV
from filter_unique_field import GenerateUniqueField
from error_frequency import ErrorFrequencyAgent
from literals import application_list, markdown_css
from re import sub


class Main:

    def __init__(self) -> None:
        self.connect = ResultAgent()
        self.gen_frequency = ErrorFrequencyAgent()
        self.load_csv = LoadCSV()
        self.convert_to_csv = EventlogtoCSV()

    def clean_source(self, option):
        return sub(r"[^a-zA-Z0-9_ \-.]", "_", option)

    def button_click(self, dictionary, index) -> None:
        how_frequent = self.gen_frequency.prompt(dictionary["TimeStamp"][index])
        prompt_string = f"""
Event ID : {dictionary["EventID"][index]}
Source : {dictionary["Source"][index]}
Entry Type : {dictionary["EntryType"][index]}
Message : {dictionary["Message"][index]}
Frequency : {how_frequent}
"""
        result = self.connect.prompt(prompt_string)
        st.markdown(
            f'<div class="result-content">{result}</div>', unsafe_allow_html=True
        )

    def generate_unique_csv(self, option):
        cleaned_option = self.clean_source(option)
        error_log_file = f"CSVfiles\\{cleaned_option}\\{cleaned_option}.csv"
        unique_log_file = f"CSVfiles\\{cleaned_option}\\unique_{cleaned_option}.csv"
        unique = GenerateUniqueField()
        unique.gen_unique(error_log_file, unique_log_file)
        return unique_log_file

    def streamlit_gui(self) -> None:
        st.set_page_config(page_title="Event Log Analyser", layout="wide")

        st.markdown(markdown_css, unsafe_allow_html=True)

        st.markdown(
            '<div class="title">Event Log Analyser</div>', unsafe_allow_html=True
        )

        option = st.selectbox("Select application", application_list)
        self.convert_to_csv.extract_evt_files(option)
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
                        st.markdown(
                            f"""
                            <div class="card">
                                <div class="card-title">EventID: {csv_dict['EventID'][i+j]}</div>
                                <div class="card-body">{csv_dict['Message'][i+j]}</div>
                            </div>
                        """,
                            unsafe_allow_html=True,
                        )

                        if st.button("Analyse", key=(i + j)):
                            self.button_click(csv_dict, (i + j))


if __name__ == "__main__":
    main = Main()
    print("main instantiated")
    main.streamlit_gui()
    print("gui instantiated")
