#!/usr/bin/env python3

import data_etl
import isbn_search


def main():
    data_etl.update_data()
    isbn_search.scanning()  # Allows scanning even if database is not updated


if __name__ == "__main__":
    main()
