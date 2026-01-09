import argparse
import csv
from pathlib import Path

import gspread
from oauth2client.service_account import ServiceAccountCredentials


CREDS_PATH = (
    "C:\\Users\\ascemama\\Documents\\Private\\Chinese\\"
    "chinese-vocabulary-storage-d11d329ddf29.json"
)


def open_spreadsheet(spreadsheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, scope)
    client = gspread.authorize(creds)
    return client.open(spreadsheet_name)


def export_rows_to_csv(spreadsheet_name, sheet_name, first_line, last_line, output_path):
    if first_line < 1 or last_line < 1:
        raise ValueError("first_line and last_line must be >= 1")
    if last_line < first_line:
        raise ValueError("last_line must be >= first_line")

    spreadsheet = open_spreadsheet(spreadsheet_name)
    worksheet = spreadsheet.worksheet(sheet_name)
    cell_range = f"B{first_line}:C{last_line}"
    rows = worksheet.get(cell_range)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        for row in rows:
            if len(row) >= 2:
                pinyin = row[0].replace(",", ".")
                translation = row[1].replace(",", ".")
                writer.writerow([pinyin, translation])
            elif len(row) == 1:
                pinyin = row[0].replace(",", ".")
                writer.writerow([pinyin, ""])
            else:
                writer.writerow(["", ""])


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Export column 2 and 3 from a Google Sheet to a CSV for Anki."
        )
    )
    parser.add_argument("spreadsheet_name", help="Google spreadsheet name")
    parser.add_argument("sheet_name", help="Worksheet/tab name")
    parser.add_argument("first_line", type=int, help="First line number (1-based)")
    parser.add_argument("last_line", type=int, help="Last line number (1-based)")
    parser.add_argument(
        "-o",
        "--output",
        help="Output CSV path",
        default=None,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(
            f"{args.spreadsheet_name}_{args.sheet_name}_"
            f"{args.first_line}_{args.last_line}.csv"
        )
    export_rows_to_csv(
        args.spreadsheet_name,
        args.sheet_name,
        args.first_line,
        args.last_line,
        output_path,
    )
    print(f"CSV exported to {output_path}")


if __name__ == "__main__":
    main()
