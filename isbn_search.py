import isbnlib
import sqlite3

# To get ANSI colors in Windows:
# import os
# os.system("color")


def scanning():
    con = sqlite3.connect("book.db")
    cur = con.cursor()

    while True:
        input_isbn = str(input("\nRead ISBN:  "))
        if input_isbn == "":
            print("\n  Quitting\n")
            break
        # Validation
        isbn13 = isbnlib.to_isbn13(input_isbn)  # Convert to isbn13 if isbn10
        if not isbnlib.is_isbn13(isbn13):
            print("\n  Not ISBN")
            continue
        # Query
        cur.execute(
            "SELECT COUNT(vapaasaldo) FROM data WHERE kuvaus=? GROUP BY kuvaus",
            (isbn13,),
        )
        result = cur.fetchall()
        if len(result) == 0:
            print("\n  Saldo = 0")
        else:
            if result[0][0] > 0:
                message = "***  SALDO = " + str(result[0][0]) + "  ***"
                print("\n  " + "\033[1;30;43m" + message + "\033[0;0m")
    cur.close()
    con.close()
