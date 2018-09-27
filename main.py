import argparse
import datetime as dt
import os
import pytz
import requests

from config import Config
from commonapp import CommonApp

from cap_sender.cap_zips import (FreshmanAppProcessor, FreshmanFormsProcessor,
                                 TransferAppProcessor, TransferAppDataProcessor,
                                 TransferEvalProcessor,
                                 TransferTranscriptProcessor)
from glob import glob
from sources import SOURCES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Custom config file.',
                        type=argparse.FileType('r'))
    parser.add_argument('-s', '--sources', nargs='*', help='Source names.')
    args = parser.parse_args()

    Config.init_config(args.config)

    cap_user = Config.get_or_else('commonapp', 'USERNAME', '')
    cap_password = Config.get_or_else('commonapp', 'PASSWORD', '')
    slate_user = Config.get_or_else('slate', 'USERNAME', '')
    slate_password = Config.get_or_else('slate', 'PASSWORD', '')
    slate_url = Config.get_or_else('slate', 'URL', '')
    timezone = Config.get_or_else('data', 'TIMEZONE', 'America/Detroit')
    out_dir = Config.get_or_else('data', 'OUT_DIR', 'data/out_dir')
    today = dt.datetime.now(pytz.timezone(timezone)).date()

    # if sources declared in arguments,
    # only handle those sources;
    # otherwise use every source
    if args.sources:
        sources = [source for source in SOURCES
                   if source.get('name') in args.sources]
    else:
        sources = SOURCES

    # prep dirs
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, f))

    # get files and save them to src
    cap = CommonApp(cap_user, cap_password)
    for source in sources:
        fn = source['pattern'].format(today.strftime(source['dttm_fmt']))
        print(f'Downloading {fn}...')
        try:
            cap.retrieve_file(filename=fn, local_path=os.path.join(out_dir, fn))
            print('Success')
        except Exception as e:
            print(f'Failure: {e}')

    # process each file
    processors = [FreshmanAppProcessor, FreshmanFormsProcessor,
                  TransferAppProcessor, TransferAppDataProcessor,
                  TransferEvalProcessor, TransferTranscriptProcessor]
    for f in os.listdir(out_dir):
        fn = os.path.join(out_dir, f)
        print(f'Processing {fn}')
        for p in processors:
            if p.match(fn):
                p.match(fn).transform()
                break

    for source in sources:
        # use glob to get all files in out_dir matching pattern
        fp = os.path.join(out_dir, source['pattern'].format('*'))
        for fn in glob(fp):
            bn = os.path.basename(fn)
            print(f"Sending {bn}...")
            url = slate_url + '/manage/service/import?cmd=load&format={}'
            r = requests.post(url.format(source['source']),
                             data=open(fn ,'rb'),
                             auth=(slate_user, slate_password))
            if r.status_code == 200:
                print('Done')
            else:
                print(f'Error: {r.status_code}')


if __name__ == '__main__':
    main()
