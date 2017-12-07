"""
Download RSNA DPS by a given poster id.
"""

import argparse
import re
import os
import pathlib
from urllib.request import urlretrieve
from urllib.error import HTTPError
import requests

SLIDE_URL = 'https://dps.rsna.org/media/{0}/presentation/images/Slide{1}.png'

def main():
    """
    Main function
    """
    # parse poster id
    parser = argparse.ArgumentParser()
    parser.add_argument('poster_id')
    parser.add_argument("-t", "--test", help="run in test mode; download only 3 slides", action="store_true")
    args = parser.parse_args()

    #poster_id = 'BR100-ED-X'
    poster_id = args.poster_id
    match = re.search(r'([a-zA-Z]+)(\d+).+', poster_id)
    subspecialty = match.group(1)

    # check if the poster exists
    first_slide_url = SLIDE_URL.format(poster_id, 1)
    r = requests.get(first_slide_url)
    if r.status_code != 200:
        print("The poster ({}) does not exist.".format(poster_id))
        return r.status_code

    # mkdirs
    downloaded_poster_path = os.path.join(os.path.dirname(__file__), '{}/{}'.format(subspecialty, poster_id))
    pathlib.Path(downloaded_poster_path).mkdir(parents=True, exist_ok=True)

    # do crawling
    reach_slides_end = False
    slide_no = 0
    while not reach_slides_end:
        slide_no += 1
        if args.test and slide_no > 3:
            break

        slide_url = SLIDE_URL.format(poster_id, slide_no)
        local_slide_path = os.path.join(downloaded_poster_path, "Slide{0}.png".format(slide_no))
        try:
            urlretrieve(slide_url, local_slide_path)
        except HTTPError as e:
            if e.code == 404:
                print('end of poster {0} at slide {1}'.format(poster_id, slide_no))
                print(e.reason)
            else:
                print('error: {0} {1}'.format(e.code, e.reason))
            reach_slides_end = True

if __name__ == '__main__':
    main()
