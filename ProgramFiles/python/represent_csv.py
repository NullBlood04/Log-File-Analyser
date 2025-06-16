import pandas as pd


class LoadCSV:

    file : str
    
    def extract_from(self, extract_file_path) -> None:
        self.file = extract_file_path
        self.data_frame = pd.read_csv(self.file)

    def display_csv(self):
        return self.data_frame


if __name__ == "__main__":

    FILE_PATH = "CSVfiles\\UniqueErrors.csv"
    loadcsv = LoadCSV()
    loadcsv.extract_from(FILE_PATH)
    file = loadcsv.display_csv()
    #print(file)
    print(type(file))
