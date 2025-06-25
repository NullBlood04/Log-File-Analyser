import csv


class GenerateUniqueField:

    def gen_unique(self, error_log_file, unique_log_file):
        try:
            event_ID = list()
            with open(error_log_file, "r") as error_log, open(unique_log_file, "a+", newline='') as unique_log:

                csv_writer = csv.writer(unique_log)
                self.error_log_reader = csv.reader(error_log)
                self.unique_log_reader = csv.reader(unique_log)

                # Checks and writes header if not present
                unique_log.seek(0, 0)
                first_char = unique_log.read(1)
                if not first_char:
                    csv_writer.writerow(["Index","TimeGenerated","EntryType","Source","EventID","Message","TimeStamp"])
                
                unique_log.seek(0, 0)
                unique_list = list()

                try:
                    for row in self.unique_log_reader:
                        event_ID.append(row[4])

                except (TypeError, IndexError) as e:
                    print("Some error occured:", e)
                
                for row in self.error_log_reader:
                    current_eventID = row[4]
                    if current_eventID not in event_ID:
                        timestamp_list = []
                        for app_row in self.error_log_reader:
                            if app_row[4] == current_eventID:
                                timestamp_list.append(app_row[1])
                        error_log.seek(0, 0)
                        row.append(f"{timestamp_list}")
                        unique_list.append(row)
                        event_ID.append(row[4])
                csv_writer.writerows(unique_list)

        except FileNotFoundError:
            with open(unique_log_file, "w") as unique_file:
                csv_writer = csv.writer(unique_file)
                csv_writer.writerow(["Index","TimeGenerated","EntryType","Source","EventID","Message","TimeStamp"])




if __name__ == "__main__":
    error_log_file = "CSVfiles\\Microsoft-Windows-Perflib\\Microsoft-Windows-Perflib.csv"
    unique_log_file = "CSVfiles\\Microsoft-Windows-Perflib\\unique_Microsoft-Windows-Perflib.csv"
    generate_unique_field = GenerateUniqueField()
    generate_unique_field.gen_unique(error_log_file, unique_log_file)