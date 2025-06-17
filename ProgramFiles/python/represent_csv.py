import pandas as pd


class LoadCSV:

    file : str
    
    def extract_from(self, extract_file_path) -> None:
        self.file = extract_file_path
        self.data_frame = pd.read_csv(self.file)

    def display_csv(self):
        return self.data_frame
    
    def display_csv_dict(self):
        return self.data_frame.to_dict()
    
    def display_row(self, event_id):
        return self.data_frame[self.data_frame["EventID"] == event_id].to_dict()


if __name__ == "__main__":

    FILE_PATH = "CSVfiles\\UniqueErrors.csv"
    loadcsv = LoadCSV()
    loadcsv.extract_from(FILE_PATH)
    file = loadcsv.display_csv_dict()
    #print(file['EventID'][0])
    print(file)
