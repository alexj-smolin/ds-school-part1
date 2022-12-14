import requests
import os
from dataclasses import dataclass
from enum import Enum


class BStatus(Enum):
    CONSTRUCT = 0
    PROBLEM = 1
    COMPLETE = 2


@dataclass
class ReadBuildingsParams:
    offset: int
    limit: int
    status: BStatus = BStatus.CONSTRUCT


@dataclass
class SavePhotosParams:
    obj_id: int
    dir_name: str


def buildings_count(status: BStatus) -> int:
    url = f'https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/api/kn/object?' \
          f'offset=0&limit=0&sortField=devId.devShortCleanNm&sortType=asc&objStatus={status.value}'
    return requests.get(url).json()['data']['total']


def read_buildings_brief(p: ReadBuildingsParams) -> list[dict]:
    url = 'https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/api/kn/object'
    params = {
        'offset': p.offset,
        'limit': p.limit,
        'sortField': 'objId',
        'sortType': 'asc',
        'objStatus': p.status.value
    }
    try:
        return requests.get(url, params).json()['data']['list']
    except Exception:
        return []


def read_building_full(obj_id: int) -> dict:
    url = f'https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/api/object/{obj_id}'
    return requests.get(url).json()['data']


def save_building_photos(p: SavePhotosParams):
    url = f'https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/api/object/{p.obj_id}'
    photos = requests.get(url).json()['data'].get('photoRenderDTO')
    if photos is None: return
    for photo in photos:
        photo_url = photo.get('objRenderPhotoUrl')
        if not photo_url: continue
        photo_name = photo.get('objRenderPhotoNm', photo_url.split('/')[-1])
        r = requests.get(photo_url, stream=True)
        if r.status_code != 200: continue
        with open(os.path.join(p.dir_name, photo_name), 'wb') as f:
            for chunk in r.iter_content(2 ** 16):
                if not chunk: break
                f.write(chunk)

