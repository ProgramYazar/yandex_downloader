import os

import requests

URL_TEMPLATE = 'https://cloud-api.yandex.net/v1/disk/public/resources?public_key={pk}&limit=10000000'


def recursive_list(public_key: str, path=''):
    files = []
    _url = URL_TEMPLATE.format(pk=public_key)
    if path != '':
        _url += '&path=' + path

    contents = requests.get(_url).json()['_embedded']['items']
    for content in contents:
        if content['type'] == 'dir':
            files.extend(recursive_list(public_key, content['path']))
        elif content['type'] == 'file':
            files.append({
                'path': os.path.join(path, content['name']).lstrip('/'),
                'url': content['file']
            })

    return files


def download_not_exists(filename: str, url: str):
    if os.path.exists(filename):
        return

    path, _file = os.path.split(filename)
    if not os.path.exists(path):
        os.makedirs(path)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


if __name__ == "__main__":
    url = input('Please enter yandex disk url: ').strip()
    files = recursive_list(url)
    for file in files:
        filename, file_url = file['path'], file['url']
        try:
            print(f"{filename} downloading...")
            download_not_exists(filename, file_url)
        except:
            print(f"!!! Error when download: {filename} !!!")
            continue
