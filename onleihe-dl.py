#!/usr/bin/env python3
import os
import subprocess
import argparse
from glob import glob
from shutil import move
from splinter import Browser, Config, exceptions
import requests
from sys import exit
from time import sleep
from random import randint
import logging
import configparser
import logging
from selenium.webdriver.firefox.service import Service

logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)

cfg = configparser.ConfigParser()
cfg.read("./onleihe-dl.cfg")

OUT_PATH = "./out/" # NOTE has to exist, include trailing slash!

def die(msg):
    logging.error(msg)
    exit(1)

def rndwait(init=False):
    sec = randint(5, 12)
    if init:
        sec = randint(0, 120)
    sleep(sec)

parser = argparse.ArgumentParser(prog="onleihe-dl.py")
parser.add_argument("-p", "--publication", required=True, type=str)
parser.add_argument("--initial-wait", action="store_true")
parser.add_argument("--sync", action="store_true")
args = parser.parse_args()

logging.info("starting run for %s", args.publication)

if args.initial_wait:
    rndwait(init=True)

logging.info("starting browser")

b_cfg = Config(fullscreen=False, headless=True)
browser = Browser("firefox", config=b_cfg)

browser.visit(cfg["onleihe"]["url"])
rndwait()
browser.find_by_text("Alle auswählen").click() # cookies
rndwait()
# sign in
browser.find_by_xpath("/html/body/header/div[1]/div/div/div[1]/a").click()

rndwait()
browser.find_by_id("userName").fill(str(cfg["onleihe"]["user"]))
rndwait()
browser.find_by_id("password").fill(str(cfg["onleihe"]["pass"]))
rndwait()
browser.find_by_value("Jetzt Anmelden").click()

rndwait()
browser.find_by_text("ePaper").click()
rndwait()

if args.publication == "zeit":
    browser.find_by_text("Die ZEIT").find_by_xpath("..").click()
elif args.publication == "fas":
    browser.find_by_text("Frankfurter Allgemeine Sonntagszeitung").find_by_xpath("..").click()
else:
    die("error: only [zeit|fas] supported")

rndwait()
browser.find_by_css("div.card-group").first.click()
rndwait()

try:
    browser.find_by_text("Jetzt ausleihen").click()
except exceptions.ElementDoesNotExist:
    die(f"error: {args.publication} daily lending limit reached")

url = browser.find_by_text("""
		Download""")._element.get_attribute("href")
logging.info("got download url: %s", url)

rndwait()
browser.quit()

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0"
}

res = requests.get(url, headers=headers, allow_redirects=True)
filename = "./.URLLink.acsm" 
open(filename, "wb").write(res.content)
logging.info("wrote acsm file: %s", filename)

realpath = os.path.realpath(filename)
subprocess.run(f"acsmdownloader -f {realpath}", shell=True, stdout=subprocess.DEVNULL)
logging.info("downloaded pdf from acsm link")

dl_files = glob("./*.pdf")
for pdf in dl_files:
    f = os.path.basename(pdf)
    cleanname = OUT_PATH + f.replace(" ", "_").replace("(", "").replace(")", "")
    move(f, cleanname)
    logging.info("moving to %s", cleanname)
    subprocess.run(f"adept_remove -f {cleanname}", shell=True)

# then rsync
if args.sync and args.publication == "zeit":
    subprocess.run(f"rsync -e 'ssh -p 23' -avzu ./out/Die_ZEIT* {cfg['rsync']['dest']}/zeit --remove-source-files", shell=True)
elif args.sync and args.publication == "fas":
    subprocess.run(f"rsync -e 'ssh -p 23' -avzu ./out/Frankfurter_Allgemeine_Sonntagszeitung* {cfg['rsync']['dest']}/fas --remove-source-files", shell=True)

logging.info("killing zombie firefox instances")
subprocess.run(f"killall firefox || true", shell=True, stdout=subprocess.DEVNULL)
