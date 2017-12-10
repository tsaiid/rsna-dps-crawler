"""
Download RSNA DPS by a given poster id.
"""

import argparse
import time
import logging
import os
import errno
import pathlib
import requests

def try_fetch_url(s, url, max_try=10, sleep_time=30):
    """
    sleep for some time to handle with ConnectionResetError
    """
    for r_count in range(max_try):
        try:
            r = s.get(url)
        except requests.exceptions.ConnectionError as err:
            logging.debug(str(err))
            if r_count >= max_try-1:
                logging.info('Retried: %s times fetching: %s', max_try, url)
            else:
                logging.info('ConnectionError, sleep: %s s, retry: %s', sleep_time, r_count)
                time.sleep(sleep_time)
        else:
            time.sleep(0.1)
            break
    return r

def download_dps2(poster_id, poster_title='', options=None):
    """
    The actual download function
    """
    slide_url_pattern = 'https://dps.rsna.org/media/{0}/presentation/images/Slide{1}.png'
    is_test_mode = True if isinstance(options, dict) and options.get('test') else False
    #poster_id = 'BR100-ED-X'
    #poster_id = options.get('poster_id', '')
    #match = re.search(r'([a-zA-Z]+)(\d+).+', poster_id)
    #subspecialty = match.group(1)
    subspecialty = poster_id[:2]

    # check if the poster exists
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})

    first_slide_url = slide_url_pattern.format(poster_id, 1)
    logging.info('first_slide_url: %s', first_slide_url)
    r = try_fetch_url(s, first_slide_url)
    if r.status_code != 200:
        print("The poster (%s) does not exist.", poster_id)
        return r.status_code

    # mkdirs
    poster_path = '{} {}'.format(poster_id, poster_title) if poster_title else poster_id
    downloaded_poster_path = os.path.join(os.path.dirname(__file__),
                                          '{}/{}'.format(subspecialty, poster_path))
    try:
        pathlib.Path(downloaded_poster_path).mkdir(parents=True, exist_ok=True)
    except OSError as e:
        if e.errno == errno.ENAMETOOLONG:
            poster_path = poster_path.split(':')[0][:255]
            downloaded_poster_path = os.path.join(os.path.dirname(__file__),
                                                  '{}/{}'.format(subspecialty, poster_path))
            pathlib.Path(downloaded_poster_path).mkdir(parents=True, exist_ok=True)

    # do crawling
    reach_slides_end = False
    slide_no = 0
    while not reach_slides_end:
        slide_no += 1
        if is_test_mode and slide_no > 3:
            break

        slide_url = slide_url_pattern.format(poster_id, slide_no)
        local_slide_path = os.path.join(downloaded_poster_path, "Slide{0}.png".format(slide_no))

        if r.url != local_slide_path:   # first slide already got
            r = try_fetch_url(s, slide_url)
        if r.status_code == 200:
            open(local_slide_path, 'wb').write(r.content)
        elif r.status_code == 404:
            logging.info('Poster %s ends at slide %d', poster_id, slide_no)
            reach_slides_end = True
        else:
            logging.error('Error: %d %s', r.status_code, r.reason)
            reach_slides_end = True
    return 0

def main():
    """
    Main function
    """
    # parse poster id
    parser = argparse.ArgumentParser()
    parser.add_argument('poster_id')
    parser.add_argument('poster_title', nargs='?')
    parser.add_argument("-t", "--test",
                        help="run in test mode; download only 3 slides",
                        action="store_true")
    parser.add_argument("-l", "--log", dest="logLevel",
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='WARNING',
                        help="Set the logging level")
    args = parser.parse_args()
    logging.basicConfig(level=logging.getLevelName(args.logLevel))

    download_dps2(args.poster_id, args.poster_title, vars(args))

if __name__ == '__main__':
    main()
