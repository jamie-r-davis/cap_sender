import argparse
import datetime as dt
import humanfriendly
import os
import paramiko
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
    parser.add_argument('-d', '--date', help='The date to pull (YYYYMMDD)')
    args = parser.parse_args()

    Config.init_config(args.config)

    cap_user = Config.get_or_else('commonapp', 'SFTP_USERNAME', '')
    cap_password = Config.get_or_else('commonapp', 'SFTP_PASSWORD', '')
    slate_user = Config.get_or_else('slate', 'USERNAME', '')
    slate_password = Config.get_or_else('slate', 'PASSWORD', '')
    slate_url = Config.get_or_else('slate', 'URL', '')
    slate_hostname = Config.get_or_else('slate', 'HOSTNAME', '')
    timezone = Config.get_or_else('data', 'TIMEZONE', 'America/Detroit')
    out_dir = Config.get_or_else('data', 'OUT_DIR', 'data/out_dir')
    if not args.date:
        today = dt.datetime.now(pytz.timezone(timezone)).date()
    else:
        today = dt.datetime.strptime(args.date, '%Y%m%d')

    # if sources declared in arguments,
    # only handle those sources;
    # otherwise use every source
    if args.sources:
        sources = [source for source in SOURCES
                   if source.get('name') in args.sources]
    else:
        sources = SOURCES

    sources.sort(key=lambda x: x['order'])

    # prep dirs
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, f))

    # get files and save them to src
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(hostname='ftp.commonapp.org',
                    port=22,
                    username=cap_user,
                    password=cap_password)
        with ssh.open_sftp() as sftp:
            for source in sources:
                fn = source['pattern'].format(today.strftime(source['dttm_fmt']))
                attr = sftp.lstat(fn)
                filesize = humanfriendly.format_size(attr.st_size)
                spinner = humanfriendly.Spinner(
                    label=f'Downloading {fn} ({filesize})',
                    total=attr.st_size,
                    hide_cursor=True)
                try:
                    sftp.get(remotepath=fn,
                             localpath=os.path.join(out_dir, fn),
                             callback=lambda x,y: spinner.step(x))
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
            filesize = humanfriendly.format_size(os.stat(fn).st_size)
            dest_path = os.path.join(source['destination'], bn)
            print(f"Sending {bn}...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=slate_hostname,
                        port=22,
                        username=slate_user,
                        password=slate_password)
            sftp = ssh.open_sftp()
            spinner = humanfriendly.Spinner(
                label=f'Sending {fn} ({filesize})',
                total=os.stat(fn).st_size,
                hide_cursor=True)
            sftp.put(fn, dest_path, callback=lambda x,y: spinner.step(x))


if __name__ == '__main__':
    main()
