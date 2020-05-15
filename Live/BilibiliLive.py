from .BaseLive import BaseLive


class BiliBiliLive(BaseLive):
    def __init__(self, room_id):
        super().__init__()
        self.room_id = room_id
        self.parsed_room_id = room_id
        self.site_name = 'BiliBili'
        self.site_domain = 'live.bilibili.com'
        self.headers['referer'] = 'https://live.bilibili.com/' + room_id

    def get_room_info(self):
        data = {}
        room_info_url = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom'
        response = self.common_request('GET', room_info_url, {'room_id': self.room_id}).json()
        if response['code'] == 0:
            data['roomname'] = response['data']['room_info']['title']
            data['site_name'] = self.site_name
            data['site_domain'] = self.site_domain
            data['status'] = response['data']['room_info']['live_status'] == 1
            self.parsed_room_id = str(response['data']['room_info']['room_id'])  # 解析完整 room_id
            data['hostname'] = response['data']['anchor_info']['base_info']['uname']
        return data

    def get_live_urls(self):
        live_urls = []
        url = 'https://api.live.bilibili.com/xlive/web-room/v1/playUrl/playUrl'
        stream_info = self.common_request('GET', url, {
            'cid': self.parsed_room_id,
            'qn': 10000,
            'platform': 'web',
            'https_url_req': 1
        }).json()
        best_quality=stream_info['data']['quality_description'][0]['qn']
        if best_quality != 10000:
            stream_info = self.common_request('GET', url, {
                'cid': self.parsed_room_id,
                'qn': best_quality,
                'platform': 'web',
                'https_url_req': 1
            }).json()
        for durl in stream_info['data']['durl']:
            live_urls.append(durl['url'])
        return live_urls
