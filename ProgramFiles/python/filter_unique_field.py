import csv


class GenerateUniqueField:

    def gen_unique(self, error_log_file, unique_log_file) -> None:
        try:
            with open(error_log_file, "r") as error_log, open(unique_log_file, "a+", newline='') as unique_log:

                self.error_log_reader = csv.reader(error_log)
                self.unique_log_reader = csv.reader(unique_log)
                unique_log.seek(0, 0)
                event_ID = list()
                unique_list = list()

                try:
                    for row in self.unique_log_reader:
                        #print(row)
                        event_ID.append(row[4])
                    #print(event_ID)
                except (TypeError, IndexError) as e:
                    print("Some error occured:", e)

                for row in self.error_log_reader:
                    if row[4] not in event_ID:
                        unique_list.append(row)
                        event_ID.append(row[4])

                csv_writer = csv.writer(unique_log)
                csv_writer.writerows(unique_list)

        except FileNotFoundError:
            with open(unique_log_file, "w") as unique_file:
                csv_writer = csv.writer(unique_file)
                csv_writer.writerow(["Index","TimeGenerated","EntryType","Source","EventID","Message"])




if __name__ == "__main__":
    error_log_file = "CSVfiles\\AppErrorLogs.csv"
    unique_log_file = "CSVfiles\\UniqueErrors.csv"
    generate_unique_field = GenerateUniqueField()
    generate_unique_field.gen_unique(error_log_file, unique_log_file)