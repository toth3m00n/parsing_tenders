import csv


def load_into_csv(tenders: list):
    """Загружает словарь с информацией о тендерах в csv"""
    with open("tenders.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=list(tenders[0].keys()), quoting=csv.QUOTE_NONNUMERIC
        )
        writer.writeheader()

        for tender in tenders:
            writer.writerow(tender)
