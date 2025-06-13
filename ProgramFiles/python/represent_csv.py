import pandas as pd


class LoadCSV:
    def __init__(self, csv_file_path: str) -> None:
        self.file = csv_file_path
    
    def extract_csv(self):
        with open(self.file, 'r') as csv_file:
            pass

    def display_csv(self):
        pass

            

