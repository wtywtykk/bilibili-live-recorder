#!/usr/bin/env python3
from Live import BiliBiliLive
import os, sys
import requests
import time
import config
import utils
import subprocess
import multiprocessing
import urllib3
import env_lang
urllib3.disable_warnings()
import random


class BiliBiliLiveRecorder(BiliBiliLive):
    def __init__(self, room_id):
        super().__init__(room_id)
        self.inform = utils.inform
        self.print = utils.print_log

    def check(self, interval):
        while True:
            try:
                room_info = self.get_room_info()
                if room_info['status']:
                    self.inform(room_id=self.room_id,desp=room_info['roomname'])
                    self.print(self.room_id, room_info['roomname'])
                    break
                else:
                    self.print(self.room_id, env_lang.get("msg.waiting"))
            except Exception as e:
                self.print(self.room_id, env_lang.get("msg.check_error") + str(e))
            time.sleep(interval*(1+random.random()))
        return self.get_live_urls()

    def record(self, record_url, output_filename):
        try:
            self.print(self.room_id, env_lang.get("msg.recording") + self.room_id)
            subprocess.call("wget -U \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36\" --referer \"https://live.bilibili.com/" + self.room_id + "\" -O \"" + output_filename + "\" \"" + record_url + "\"",shell=True)
        except Exception as e:
            self.print(self.room_id, env_lang.get("msg.record_error") + str(e))

    def run(self):
        while True:
            try:
                urls = self.check(interval=config.check_interval)
                filename = utils.generate_filename(self.room_id)
                c_directory=os.path.join(os.getcwd(), 'files')
                if not os.path.exists(c_directory):
                    os.makedirs(c_directory)
                c_filename = os.path.join(c_directory, filename)
                self.record(urls[0], c_filename)
                self.print(self.room_id, env_lang.get("msg.finish") + c_filename)
            except Exception as e:
                self.print(self.room_id, env_lang.get("msg.run_error") + str(e))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        input_id = [str(sys.argv[1])]
    elif len(sys.argv) == 1:
        input_id = config.rooms  # input_id = '917766' '1075'
    else:
        raise ZeroDivisionError(env_lang.get("msg.parameter_error"))

    mp = multiprocessing.Process
    tasks = [mp(target=BiliBiliLiveRecorder(room_id).run) for room_id in input_id]
    for i in tasks:
        i.start()
    for i in tasks:
        i.join()
