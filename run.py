#!/usr/bin/env python3
from Live import BiliBiliLive
import os, sys, shutil
import requests
import time
import config
import subprocess
import multiprocessing
import urllib3
import env_lang
urllib3.disable_warnings()
import random
import traceback

class RecordFilePath:
    def __init__(self, basedir, foldername):
        t = time.time()
        current_struct_time = time.localtime(t)
        current_time = time.strftime('%Y%m%d_%H%M', current_struct_time)
        self.timestamp = current_time + '-' + str(int(round(t * 1000)))
        self.basedir = basedir
        self.foldername = foldername

    def get(self, extension):
        c_directory=os.path.join(self.basedir, 'files', self.foldername)
        if not os.path.exists(c_directory):
            os.makedirs(c_directory)
        return os.path.join(c_directory, self.timestamp + extension)

    def get_temp(self, extension):
        c_directory=os.path.join(self.basedir, 'tmp', self.foldername)
        if not os.path.exists(c_directory):
            os.makedirs(c_directory)
        return os.path.join(c_directory, self.timestamp + extension)

class AudioConverter:
    def __init__(self, output_path):
        self.output_path = output_path

    def run(self):
        subprocess.call(config.ffmpeg_path + " -y -i \"" + self.output_path.get(".flv") + "\" -acodec mp3 -vn \"" + self.output_path.get_temp(".mp3") + "\"",shell=True)
        shutil.move(self.output_path.get_temp(".mp3"), self.output_path.get(".mp3"))

class BiliBiliLiveRecorder(BiliBiliLive):
    def __init__(self, room_id):
        super().__init__(room_id)

    def print(self, content='None'):
        t = time.time()
        current_struct_time = time.localtime(t)
        brackets = '[{}]'
        time_part = brackets.format(time.strftime('%Y-%m-%d %H:%M:%S', current_struct_time))
        room_part = brackets.format(env_lang.get('label.living_room') + self.room_id)
        print(time_part, room_part, content)

    def check(self, interval):
        while True:
            try:
                room_info = self.get_room_info()
                if room_info['status']:
                    self.print(room_info['roomname'])
                    break
                else:
                    self.print(env_lang.get("msg.waiting"))
            except Exception as e:
                self.print(env_lang.get("msg.check_error") + repr(e))
                traceback.print_exc()
            time.sleep(interval*(1+random.random()))
        return self.get_live_urls()
        
    def savename(self, output_path):
        try:
            room_info = self.get_room_info()
            file_obj = open(output_path.get(".txt"),"w",True,"utf-8")
            file_obj.write(room_info['roomname'])
            file_obj.close();
        except Exception as e:
            self.print(env_lang.get("msg.run_error") + repr(e))
            traceback.print_exc()

    def record(self, record_url, output_path):
        try:
            self.print(env_lang.get("msg.recording") + self.room_id)
            record_path=output_path.get(".flv")
            subprocess.call("wget --timeout=5 -t 2 -U \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36\" --referer \"https://live.bilibili.com/" + self.room_id + "\" -O \"" + record_path + "\" \"" + record_url + "\"",shell=True)
            time.sleep(1)
            if os.path.exists(record_path):
                if os.path.getsize(record_path):
                    if config.rooms[self.room_id] in config.convert_rooms:
                        if len(config.ffmpeg_path):
                            convert_task = multiprocessing.Process(target=AudioConverter(output_path).run)
                            convert_task.start()
                    self.savename(output_path)
                else:
                    os.remove(record_path)
        except Exception as e:
            self.print(env_lang.get("msg.record_error") + repr(e))
            traceback.print_exc()

    def run(self):
        while True:
            try:
                urls = self.check(interval=config.check_interval)
                self.record(urls[0], RecordFilePath(os.getcwd(),config.rooms[self.room_id]))
                self.print(env_lang.get("msg.finish") + self.room_id)
            except Exception as e:
                self.print(env_lang.get("msg.run_error") + repr(e))
                traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        input_id = [str(sys.argv[1])]
    elif len(sys.argv) == 1:
        input_id = config.rooms.keys()
    else:
        raise ZeroDivisionError(env_lang.get("msg.parameter_error"))

    mp = multiprocessing.Process
    tasks = [mp(target=BiliBiliLiveRecorder(room_id).run) for room_id in input_id]
    for i in tasks:
        i.start()
    for i in tasks:
        i.join()
