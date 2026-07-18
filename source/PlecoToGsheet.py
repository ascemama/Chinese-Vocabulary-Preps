from dataclasses import dataclass, field
from typing import Callable

from sqlLite import closeDB, openDB, updateDBWithNewWordFromPleco


@dataclass
class PlecoProcessingStatistics:
    total_entries: int
    processed_entries: int = 0
    already_in_db: int = 0
    not_in_db: int = 0
    changed_in_db: int = 0


@dataclass
class PlecoProcessingResult:
    rows: list[list[str]] = field(default_factory=list)
    statistics: PlecoProcessingStatistics = field(
        default_factory=lambda: PlecoProcessingStatistics(total_entries=0)
    )
    should_upload: bool = True


def _percentage(value, total):
    if total == 0:
        return 0.0
    return value / total * 100


def format_statistics(statistics):
    total = statistics.total_entries
    processed = statistics.processed_entries
    return "\n".join(
        [
            "\n===== Pleco import statistics =====",
            f"Total entries in pleco.txt: {total} ({_percentage(total, total):.1f}%)",
            (
                f"Entries processed: {processed} "
                f"({_percentage(processed, total):.1f}%)"
            ),
            (
                f"Initially already in DB: {statistics.already_in_db} "
                f"({_percentage(statistics.already_in_db, processed):.1f}%)"
            ),
            (
                f"Initially not in DB: {statistics.not_in_db} "
                f"({_percentage(statistics.not_in_db, processed):.1f}%)"
            ),
            (
                f"Already in DB but changed: {statistics.changed_in_db} "
                f"({_percentage(statistics.changed_in_db, processed):.1f}%)"
            ),
            "===================================",
        ]
    )


def print_statistics(statistics):
    print(format_statistics(statistics))


def _get_existing_translation(pinyin, cursor, table_name):
    cursor.execute(
        f"SELECT translation FROM {table_name} WHERE source = ? LIMIT 1;",
        (pinyin,),
    )
    row = cursor.fetchone()
    if row is None:
        return False, None
    return True, row[0]


def process_chinese_pleco_file(file_path, cursor, connection, table_name):
    with open(file_path, "r", encoding="utf-8") as file:
        entries = [line for line in file if line.strip()]

    statistics = PlecoProcessingStatistics(total_entries=len(entries))
    result = PlecoProcessingResult(statistics=statistics)

    for index, line in enumerate(entries, start=1):
        parts = line.split()
        pinyin = parts[1].strip()
        chinese_char = parts[0].strip()
        pleco_traduction = " ".join(parts[3:]).strip()

        was_in_db, existing_translation = _get_existing_translation(
            pinyin, cursor, table_name
        )
        statistics.processed_entries += 1
        if was_in_db:
            statistics.already_in_db += 1
        else:
            statistics.not_in_db += 1

        print(
            f"\n ----- {index}/{statistics.total_entries} ----- "
            f"\n{pinyin} -- {pleco_traduction}"
        )
        traduction = updateDBWithNewWordFromPleco(
            chinese_char,
            pinyin,
            pleco_traduction,
            cursor,
            connection,
            table_name,
        )

        if (
            was_in_db
            and traduction not in {"x", "y", "z"}
            and traduction != existing_translation
        ):
            statistics.changed_in_db += 1

        if traduction == "y":
            result.should_upload = False
            return result
        if traduction not in {"x", "z"}:
            result.rows.append([pinyin, traduction])
        if traduction == "z":
            return result

    return result


def upload_if_requested(
    result: PlecoProcessingResult,
    uploader: Callable,
    spreadsheet_name,
    worksheet_name,
):
    if not result.should_upload:
        return False

    print("Upload to google sheet")
    uploader(result.rows, spreadsheet_name, worksheet_name)
    print("Done !")
    return True


def main():
    from gSheetHelper import CurrentChineseWorksheet, upload_to_google_sheet

    file_path = "source/pleco.txt"
    cursor, connection = openDB()
    print(connection)
    try:
        result = process_chinese_pleco_file(
            file_path, cursor, connection, "chinese"
        )
    finally:
        closeDB(cursor, connection)

    try:
        upload_if_requested(
            result,
            upload_to_google_sheet,
            "ChineseVocab",
            CurrentChineseWorksheet,
        )
    finally:
        print_statistics(result.statistics)


if __name__ == "__main__":
    main()
