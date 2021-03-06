"""
Bulk download RSNA DPS Poster by given CSV file and subspecialities.
"""

import argparse
import logging
import csv
import download_dps2

def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_file')
    parser.add_argument('categories', nargs='*')
    parser.add_argument("-t", "--test", help="run in test mode; download only 3 slides", action="store_true")
    parser.add_argument("-l", "--log", dest="logLevel",
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='WARNING',
                        help="Set the logging level")
    args = parser.parse_args()
    logging.basicConfig(level=logging.getLevelName(args.logLevel))

    #print(args.categories)
    csv_file = args.csv_file
    categories = args.categories

    # read csv file
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        if args.test:
            print('In TEST mode, only 3 slides per poster will be downloaded.')
        for row in reader:
            #print(row['poster_id'], row['title'])
            poster_cat = row['poster_id'][:2]
            if not categories or poster_cat in categories:
                print('Start downloading: ', row['poster_id'], row['title'])
                download_dps2.download_dps2(row['poster_id'], row['title'], vars(args))

if __name__ == '__main__':
    main()
