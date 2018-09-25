import argparse
import datetime as dt
import os
import requests
from config import Config
from commonapp import CommonApp
from cap_sender import process_zips
from glob import glob


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Custom config file.',
                        type=argparse.FileType('r'))
    args = parser.parse_args()

    Config.init_config(args.config)

    cap_user = Config.get_or_else('commonapp', 'USERNAME', '')
    cap_password = Config.get_or_else('commonapp', 'PASSWORD', '')
    slate_user = Config.get_or_else('slate', 'USERNAME', '')
    slate_password = Config.get_or_else('slate', 'PASSWORD', '')
    slate_url = Config.get_or_else('slate', 'URL', '')
    src_dir = Config.get_or_else('data', 'SRC_DIR', 'data/src')
    out_dir = Config.get_or_else('data', 'OUT_DIR', 'data/out_dir')
    sources = Config.get_or_else('data', 'SOURCES', '')
    sources = [v.split(':') for v in sources.split(' ')]
    patterns = [x[0] for x in sources]
    filenames = [x.format(dt.date.today().strftime('%m%d%Y')) for x in patterns]

    # get files and save them to src
    cap = CommonApp(cap_user, cap_password)
    for fn in filenames:
        cap.retrieve_file(filename=fn, local_path=os.path.join(src_dir, fn))

    # flatten xml files to csv, place output in out_dir
    process_zips(src_dir, out_dir)

    for pattern, guid in sources:
        # use glob to get all files in out_dir matching pattern
        fp = os.path.join(out_dir, pattern.format('*'))
        for fn in glob(fp):
            bn = os.path.basename(fn)
            print(f"Sending {bn}...)")
            url = slate_url + '/manage/service/import?cmd=load&format={}'
            r = requests.post(url.format(guid),
                             data=open(fn ,'rb'),
                             auth=(slate_user, slate_password))
            if r.status_code == 200:
                print('Done')
            else:
                print(f'Error: {r.status_code}')
            os.remove(fn)

    # cleanup
    for fp in glob(os.path.join(src_dir, '*')):
        os.remove(fp)
    for fp in glob(os.path.join(out_dir, '*')):
        os.remove(fp)

if __name__ == '__main__':
    main()
