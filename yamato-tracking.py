# -*- coding: utf-8 -*-
import sys
import time
import io
import threading
import ssl

import schedule
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageEnhance
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from bs4 import BeautifulSoup
from win11toast import notify

INTERVAL = 60


class YamatoAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('@SECLEVEL=2:ECDH+AESGCM:ECDH+CHACHA20:ECDH+AES:DHE+AES:AESGCM:!aNULL:!eNULL:!aDSS:!SHA1:!AESCCM:!PSK')
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLSv1_2,
            ssl_context=ctx,
        )


class taskTray:
    def __init__(self, codes):
        # 追跡番号
        self.codes = codes
        # 通知済みフラグ
        self.notified = False
        # スレッド実行モード
        self.running = False
        self.session = requests.Session()
        self.session.mount('https://', YamatoAdapter())

        # from favicon
        base = 'https://www.kuronekoyamato.co.jp'
        soup = BeautifulSoup(self.session.get(base).content, 'html.parser')
        href = soup.find('link', rel='apple-touch-icon-precomposed').get('href')
        self.icon_image = Image.open(io.BytesIO(self.session.get(base + href).content))
        self.dimm_image = ImageEnhance.Brightness(self.icon_image).enhance(0.5).convert('L')

        menu = Menu(
            MenuItem('Check', self.doCheck),
            MenuItem('Exit', self.stopApp),
        )
        self.app = Icon(name='PYTHON.win32.yamato', title='kuronekoyamato checker', icon=self.dimm_image, menu=menu)
        self.doCheck()

    def doCheck(self):
        lines = []
        count = 0
        icon = self.dimm_image

        for code in self.codes:
            url = 'https://toi.kuronekoyamato.co.jp/cgi-bin/tneko'
            with self.session.post(url, data={'number01': code}) as r:
                title = f'{code} 未登録'
                soup = BeautifulSoup(r.content, 'html.parser')
                st = soup.find('div', class_='tracking-invoice-block-detail')
                if st:
                    stat = st.find_all('li')[-1].find_all('div')
                    _stat = stat[0].text
                    _time = stat[1].text
                    _name = stat[2].text
                    title = f'{code} {_stat} {_time} {_name}'
                    if _stat == '配達完了':
                        if self.notified is False:
                            self.notified = True
                            notify(
                                body=title,
                                audio='ms-winsoundevent:Notification.Reminder',
                            )
                        count = count + 1
                lines.append(title)

        if count:
            icon = self.icon_image

        self.app.title = '\n'.join(lines)
        self.app.icon = icon
        self.app.update_menu()

    def runSchedule(self):
        schedule.every(INTERVAL).seconds.do(self.doCheck)

        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stopApp(self):
        self.running = False
        self.app.stop()

    def runApp(self):
        self.running = True

        task_thread = threading.Thread(target=self.runSchedule)
        task_thread.start()

        self.app.run_detached()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        codes = []
        for code in sys.argv[1:]:
            code = code.replace('-', '')
            if len(code) == 12 and str(int(code)) == code:
                codes.append(code)
        taskTray(codes).runApp()
    else:
        print(f'{sys.argv[0]} <tracking code ...>')
        exit(1)
