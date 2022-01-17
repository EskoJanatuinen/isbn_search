import os
import requests
import zipfile
import sqlite3
import pandas as pd
import isbnlib
from dotenv import load_dotenv
from datetime import date


load_dotenv()
url = os.getenv("ISBN_URL")
pwd = os.getenv("ISBN_PWD")


def update_data():
    """Downloads product list (zip)"""
    # Note: file contains only Kierrätyskeskus products (warehouse = 10)
    try:
        file = open("last_run.tmp", "r")
    except FileNotFoundError:
        open("last_run.tmp", "x").close()
        file = open("last_run.tmp", "r")
    finally:
        last_download = file.readline()
        file.close()
    if str(date.today()) != last_download:
        print("\nDownloading data...")
        try:
            r = requests.get(url, allow_redirects=False, timeout=(5, 15))
        except Exception as e:
            print(e)
        try:
            with open("last_run.tmp", "w") as f:
                f = open("dump.zip", "wb").write(r.content)
                print("Data downloaded")
                if extract():
                    update_db()
                    update_date()
        except Exception as e:
            print(e)


def extract():
    """Extracts the zip"""
    if pwd is None:
        print("Database was not updated:")
        print("Password is missing from env variables.")
        return False
    try:
        with zipfile.ZipFile("dump.zip") as f:
            f.extractall(pwd=bytes(pwd, "cp1252"))
        return True
    except Exception as e:
        print("Database was not updated:")
        print(e)
        return False


def update_date():
    """Saves the download date"""
    try:
        with open("last_run.tmp", "w") as f:
            f.write(str(date.today()))
    except Exception as e:
        print(e)


def update_db():
    """Reading tuotedumb.csv to sqlite"""
    df = pd.read_csv("tuotedump.csv", on_bad_lines="skip", encoding="cp1252")
    df = df[df["Passiivinen"] == False]  # Select active products
    df = df[df["Verkkokauppa"] == True]  # Select online products
    df = df.drop(df.columns[[0, 1, 2, 3, 6, 7]], axis=1)  # Remove unused columns
    df.fillna("empty", inplace=True)  # Remove NaN values

    print("\nReading data...")
    for i in range(len(df)):
        if len(isbnlib.get_isbnlike(df.iloc[i, 0], level="normal")) > 0:
            isbn = isbnlib.get_isbnlike(df.iloc[i, 0], level="normal")[0]
            isbn13 = isbnlib.to_isbn13(isbn)
            df.iloc[i, 0] = isbn13
        else:
            df.iloc[i, 0] = "missing"

    db = df[df["kuvaus"] != "missing"]  # Drop rows, if ISBN is missing
    db.reset_index(drop=True, inplace=True)  # Reset index

    try:
        con = sqlite3.connect("book.db")
        db.to_sql("data", con, if_exists="replace")
    except Exception as e:
        print(e)
    finally:
        con.close()
        print("Database updated")
