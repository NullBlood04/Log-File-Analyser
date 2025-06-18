# Local imports
from Log_to_Csv import EventlogtoCSV
from filter_unique_field import GenerateUniqueField
from StreamlitGUI import StreamlitRendering

        

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