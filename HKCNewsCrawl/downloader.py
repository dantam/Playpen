#!/usr/local/bin/python3

import argparse

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request

def get_args():
    parser = argparse.ArgumentParser(
        description="Extract prisoner status from website",
    )
    parser.add_argument(
        '--base_url',
        help='URL to crawl from',
        default='https://www1.hkcnews.com/legalcasedb/profiles',
    )
    parser.add_argument(
        '--cache_file',
        help='file storing local copy of profile page',
        default='/tmp/hkcnews.legalcasedb.html',
    )
    parser.add_argument(
        '--skip_cache',
        help='download even when cache file exists',
        action='store_true',
        default=False,
    )
    parser.add_argument(
        '--out_file',
        help='output file name',
        default='/tmp/hkcnews.tsv',
    )
    parser.add_argument(
        '--col_delim',
        help='column delimiter',
        default='\t',
    )
    return parser.parse_args()

class PageManager():
    def __init__(self, args):
        self.args = args
        self.event_class = {'class': 'col-12 accevents'}
        self.charge_class = {'class': 'col-12 p-0 pt-1 charge pb-1 mb-1'}
        self.hkc_base_url = 'www1.hkcnews.com'

    def download_file(self):
        try:
            f = open(self.args.cache_file)
            content = f.read()
        except:
            content = None

        if content == None or self.args.skip_cache:
            req = Request(
                self.args.base_url,
                headers={'User-Agent': 'Mozilla/5.0'},
            )
            content = urlopen(req).read()

            with open(self.args.cache_file, 'wb') as cfile:
                cfile.write(content)
        return content

    def parse_file(self, content):
        if content == None:
            with open(self.args.cache_file) as f:
                content = f.read()

        soup = BeautifulSoup(content, "html.parser")
        profiles = soup.find_all('a', {'class': 'profileWrap'})
        values = []
        for profile in profiles:
            profile_url = self.hkc_base_url + '/' + profile['href']
            name = profile.find('h2').find(text=True)
            events = profile.find_all('div', self.event_class)
            for event in events:
                charges = profile.find_all('div', self.charge_class)
                event_name = event.find('p').find(text=True)
                for charge in charges:
                    texts = charge.findAll(text=True)
                    charge_details = [t for t in texts if t.strip()]
                    charge = charge_details[0]
                    statuses = ','.join(charge_details[1:])
                    current_status = charge_details[-1]
                    vals = [
                        name,
                        profile_url,
                        event_name,
                        charge,
                        current_status,
                        statuses,
                    ]
                    values.append(vals)
        return values

    def write_file(self, values):
        header = [
            'person_name',
            'profile_url',
            'event_name',
            'charge',
            'last_status_for_charge',
            'statuses_for_charge',
        ]
        with open(self.args.out_file, 'w') as f:
            lines = [self.args.col_delim.join(header)]
            for v in values:
                lines.append(self.args.col_delim.join(v))
            f.write('\n'.join(lines))

    def run(self):
        content = self.download_file()
        values = self.parse_file(content)
        self.write_file(values)

def main():
    m = PageManager(get_args())
    m.run()

if __name__ == '__main__':
    main()
