import argparse
import requests
import time

from config import Config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Custom config file.',
                        type=argparse.FileType('r'))
    args = parser.parse_args()
    Config.init_config(args.config)
    slate_user = Config.get_or_else('slate', 'USERNAME', '')
    slate_password = Config.get_or_else('slate', 'PASSWORD', '')
    slate_url = Config.get_or_else('slate', 'URL', '')
    slate_source = Config.get_or_else('webadmit', 'PAYMENT_SOURCE', '')
    wa_api_key = Config.get_or_else('webadmit', 'API_KEY', '')
    wa_user_id = Config.get_or_else('webadmit', 'USER_ID', '')
    wa_payment_export = Config.get_or_else('webadmit', 'PAYMENT_EXPORT', '')
    wa_url = 'https://api.webadmit.org'

    print(wa_api_key, wa_user_id, wa_payment_export)

    s = requests.session()
    s.headers['x-api-key'] = wa_api_key

    # trigger the export
    url = wa_url + '/api/v1/user_identities/{user_id}/exports/{export_id}/export_files'
    r = s.post(url.format(user_id=wa_user_id, export_id=wa_payment_export))
    assert r.status_code == 200
    while True:
        r = s.get(url.format(user_id=wa_user_id, export_id=wa_payment_export))
        if r.json()['export_files'][0]['status'] == 'Available':
            break
        time.sleep(3)
    href = r.json()['export_files'][0]['href']
    r2 = s.get(wa_url + href)
    assert r2.status_code == 200
    download_url = r2.json()['export_files']['download_url']
    r3 = s.get(download_url)
    # send to slate
    slate_endpoint = slate_url+'/manage/service/import?cmd=load&format={}'
    r4 = s.post(slate_endpoint.format(slate_source),
                data=r3.content,
                auth=(slate_user, slate_password))


if __name__ == '__main__':
    main()
