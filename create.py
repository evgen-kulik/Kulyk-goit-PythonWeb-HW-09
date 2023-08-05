"""
Передача даних (зі створенням колекцій author та quote) до БД hw_09
з файлів authors.json та quotes.json. Опис моделей виконано в models.py.
"""


from models import Author, Quote
import json


if __name__ == "__main__":
    # прочитаємо .json
    with open("authors.json", "r", encoding="utf-8") as fh:
        data_authors = json.load(fh)
    with open("quotes.json", "r", encoding="utf-8") as fh:
        data_quotes = json.load(fh)

    # запишемо дані в БД (.save())
    for i in range(0, len(data_authors)):
        Author(
            fullname=data_authors[i]["fullname"],
            born_date=data_authors[i]["born_date"],
            born_location=data_authors[i]["born_location"],
            description=data_authors[i]["description"],
        ).save()
    for i in range(0, len(data_quotes)):
        quote = Quote(
            tags=data_quotes[i]["tags"],
            author=data_quotes[i]["author"],
            quote=data_quotes[i]["quote"],
        ).save()
