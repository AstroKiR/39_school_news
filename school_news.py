#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 00:11:19 2020

@author: astrok
"""
from bs4 import BeautifulSoup
from datetime import datetime
from subprocess import call
import notify2
import pickle
import requests
import logging
import time
import sys
import os

main_path = os.path.abspath(os.path.dirname(sys.argv[0]))

today = datetime.now()
current_day = today.strftime('%Y_%m_%d')
logging_format = '%(asctime)s - %(levelname)s [%(filename)s:%(lineno)d] - %(message)s'
logging.basicConfig(
    filename=f'{main_path}/logs/{current_day}.log',
    level=logging.INFO,
    format=logging_format)


def show_popup(urgency, init_string, header, message):
    notify2.init(init_string)
    n = notify2.Notification(header, message)
    if urgency == 'CRITICAL':
        n.set_urgency(notify2.URGENCY_CRITICAL)
    elif urgency == 'NORMAL':
        n.set_urgency(notify2.URGENCY_NORMAL)
    else:
        n.set_urgency(notify2.URGENCY_LOW)
    n.show()


def main():
    dt_now = datetime.now()
    response = requests.get('http://nsch39.minsk.edu.by/')
    soup = BeautifulSoup(response.text, 'html.parser')
    news = soup.find_all(class_='nameNews')

    pfile = f'{main_path}/.news'

    try:
        with open(pfile, 'rb') as opf:
            old_news = pickle.load(opf)
    except FileNotFoundError:
        with open(pfile, 'wb') as emptyf:
            pickle.dump((), emptyf)
            old_news = ()

    new_news = []

    for new in news:
        new_date = new.text
        new_name = new.parent.next_sibling.next_sibling.text
        new_news.append((new_date, new_name))

    with open(pfile, 'wb') as npf:
        pickle.dump(new_news, npf)

    old_news = set(old_news)
    new_news = set(new_news)

    diff = new_news.difference(old_news)

    show_popup('NORMAL', '39 SCHOOL NEWS:D', 'INFO', f'new request: {dt_now}')

    if diff:
        for d in diff:
            show_popup('CRITICAL', '39 SCHOOL NEWS:D', d[0], d[1])
            call(f"/usr/bin env telegram-send '{d[0]}: {d[1]}'", shell=True)
            logging.info(f'{d[0]}: {d[1]}')


if __name__ == '__main__':
    time.sleep(120)
    main()
