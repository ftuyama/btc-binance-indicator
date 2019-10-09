#!/usr/bin/env python3

import subprocess
import os
import signal
import gi
import time
import locale
import time
import sys

from api.api import Api
from api.websocket import Websocket
from utils.image import ImageUtil

locale.setlocale(locale.LC_ALL, '')
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk, AppIndicator3
from gi.repository import Notify as notify
from threading import Thread

currpath = os.path.dirname(os.path.realpath(__file__))

coins = ['btc', 'eth', 'ae', 'link', 'eos', 'ht', 'dock', 'egt']
sources = ['Binance', 'Binance Futures', 'Huobi']

class Indicator():
    def __init__(self):
        self.api = Api()
        self.websocket = Websocket()
        self.image_util = ImageUtil("btcf")

        self.update = None
        self.source = sources[1]
        self.symbol = 'btcusdt'
        self.app = 'update_setting'

        self.path = currpath
        self.indicator = AppIndicator3.Indicator.new(
            self.app, currpath + "/icons/btc.png",
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.create_menu()

        self.start_source()

        notify.init(self.app)

    def start_source(self):
        # if self.update is not None:
        #     self.update._stop()
        #     self.update = None

        if self.source == 'Binance Futures':
            self.indicator.set_icon(currpath + "/icons/btcf.png")
            self.update = Thread(target=self.websocket.start_ws, args=[self])
            self.update.start()
        else:
            self.update = Thread(target=self.background_monitor)
            self.update.setDaemon(True)
            self.update.start()

    """Menu methods

        These methods handle menu interaction
    """
    def create_menu(self):
        self.menu = Gtk.Menu()

        group = []
        for source in sources:
            item = Gtk.RadioMenuItem.new_with_label(group, source)
            group = item.get_group()
            item.connect('activate', self.select_source)
            self.menu.append(item)

        self.menu.append(Gtk.SeparatorMenuItem())

        group = []
        for coin in coins:
            item = Gtk.RadioMenuItem.new_with_label(group, coin.upper() + '/USDT')
            group = item.get_group()
            item.connect('activate', self.select_coin)
            self.menu.append(item)

        # quit
        item_quit = Gtk.MenuItem('Quit')
        sep = Gtk.SeparatorMenuItem()
        self.menu.append(sep)
        item_quit.connect('activate', self.stop)
        self.menu.append(item_quit)
        self.menu.show_all()

        self.indicator.set_menu(self.menu)

        return self.menu

    def select_source(self, item):
        self.source = item.get_label()
        self.start_source()

    def select_coin(self, item):
        coin = item.get_label().split('/')[0].lower()
        self.symbol = coin + 'usdt'
        self.indicator.set_icon(currpath + "/icons/" + coin + ".png")

    """Core methods

        These methods do a lot of stuff
    """
    def background_monitor(self):
        symbol_price = self.api.huobi_symbol_price(self.symbol)
        mark_price = symbol_price
        print(f"### start {self.source} monitor ###")

        while True:
            change = ''
            last_price = symbol_price
            monitor = self.api.binance_symbol_avg_price if self.source == 'Binance' else self.api.huobi_symbol_price
            symbol_price = monitor(self.symbol) or last_price

            mark_price = self.check_alert(symbol_price, mark_price)

            self.indicator.set_label(' $' + f'{symbol_price:n}' + change, '')
            time.sleep(1)

    def check_alert(self, price, mark_price):
        delta = 100.0 * (price - mark_price) / mark_price
        gain = 0.3 if self.symbol == 'btcusdt' else 1.0

        if delta > gain or delta < -1 * gain:
            self.alert(delta, price)
            return price

        return mark_price

    def alert(self, delta, price):
        date = time.strftime("%Y-%m-%d %H:%M:%S")
        price_label = ' $' + f'{price:n}'
        delta_label = f'{delta:n}' + ' %'
        notify.Notification.new(self.symbol + " " + price_label, delta_label + " on " + date, None).show()

    def stop(self, _arg):
        Gtk.main_quit()
        sys.exit(0)


Indicator()
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()
