# Library imports
from langchain.schema import SystemMessage, HumanMessage

# Local imports
from Log_to_Csv import EventlogtoCSV
from represent_csv import LoadCSV
from AI_handler import Connect_AI
import streamlit as st

        
class StreamlitRendering:

    def streamlit_gui(self) -> None:
        pass


class Main:

    def main(self) -> None:
        #connect = Connect_AI()
        load_csv = LoadCSV()
        convert_to_csv = EventlogtoCSV("Microsoft-Windows-Perflib")
        convert_to_csv.extract_evt_files()
        load_csv.extract_from("CSVfiles\\UniqueErrors.csv")
        st.set_page_config(page_title="Event Log Analyser", layout="wide")
        st.title("Event Log Analyser")
        st.dataframe(load_csv.display_csv())


if __name__ == "__main__":
    main = Main()
    main.main()