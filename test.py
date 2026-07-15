import csv

file_path = "data/current_elo_ratings.csv"

with open(file_path, encoding="utf-8") as file:
    reader = csv.reader(file)

    header = next(reader)
    expected_fields = len(header)

    print(f"Expected fields per row: {expected_fields}")

    for line_number, row in enumerate(reader, start=2):
        if len(row) != expected_fields:
            print(
                f"Line {line_number}: "
                f"expected {expected_fields}, found {len(row)}"
            )
            print(row)