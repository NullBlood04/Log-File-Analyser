# Local imports
from Log_to_Csv import EventlogtoCSV
from represent_csv import LoadCSV
from AI_handler import Connect_AI
import streamlit as st
from filter_unique_field import GenerateUniqueField

        
class StreamlitRendering:


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
        st.markdown(result) # TODO: change this to stylise


    def streamlit_gui(self) -> None:

        self.load_csv.extract_from("CSVfiles\\UniqueErrors.csv")
        st.set_page_config(page_title="Event Log Analyser", layout="wide")
        st.title("Event Log Analyser")

        st.dataframe(self.load_csv.display_csv())
        csv_dict = self.load_csv.display_csv_dict()

        timegendict = csv_dict["TimeGenerated"]
        count = timegendict
        button = []
        for key in count:
            button.append(st.button(label=csv_dict["Message"][key]))

        for i, each_button in enumerate(button):
            if each_button:
                self.button_click(csv_dict, i)



class Main:
        

    def main(self) -> None:
        convert_to_csv = EventlogtoCSV("Microsoft-Windows-Perflib")
        convert_to_csv.extract_evt_files()
        unique_csv = GenerateUniqueField()
        unique_csv.gen_unique()

        gui = StreamlitRendering()
        gui.streamlit_gui()

        

if __name__ == "__main__":
    main = Main()
    main.main()