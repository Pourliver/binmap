#/bin/python3
import subprocess
import configparser
import argparse
import os.path
import string
import sys
import re

# TODO
# THREADS!!!
# wrap under a main function
# make everything more readable
# make a great description
# custom wordlist
# handle errors

parser = argparse.ArgumentParser(description='ADD NAME')
parser.add_argument('file', metavar='file', help='The file to execute')
parser.add_argument('--x64', action='store_true', help='Toggles the x64 mode')
parser.add_argument('-w', '--wordlist', help='The list of caracters to use (minimum 2 caracters)')
config = configparser.ConfigParser()
args = parser.parse_args()
BINMAP_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = f'{BINMAP_PATH}/config.ini'
WORDLIST = args.wordlist if args.wordlist else string.printable
FILE = args.file
MIN_COUNT = 0
flag = ''
found = False

if (os.path.exists(CONFIG_PATH)):
    config.read(CONFIG_PATH)
    PIN_FOLDER = config['DEFAULT']['pin_folder']
else:
    PIN_FOLDER = input('Enter your pin install path [/opt/pin] : ') or "/opt/pin"
    config['DEFAULT'] = {'pin_folder' : PIN_FOLDER}
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)

if args.x64:
    SO_PATH = f"{PIN_FOLDER}/obj-intel64/opcodemix.so"
else:
    SO_PATH = f"{PIN_FOLDER}/obj-ia32/inscount0.so"

if args.wordlist:
    if len(args.wordlist) < 2:
        parser.error("A wordlist needs a least 2 caracters.")
    WORDLIST = args.wordlist    
else:
    WORDLIST = string.printable


def pin(data):
    global FILE
    count_regex = b'Count ([0-9]*)\n$'
    output = ''
    try:
        p = subprocess.Popen(['pin', '-t', SO_PATH, '-o', '/dev/stdout', '--', FILE], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = p.communicate(input=data.encode('UTF-8'))[0]
    except subprocess.CalledProcessError as e:
        exit(0)

    count = int(re.search(count_regex, output).groups()[0])
    return count

def setup():
    global MIN_COUNT, flag
    case1 = pin(flag + WORDLIST[0])
    case2 = pin(flag + WORDLIST[1])

    MIN_COUNT = min([case1, case2])
setup()
while not found:
    for letter in WORDLIST:
        candidate = flag + letter
        count = pin(candidate)
        
        if count > MIN_COUNT:
            flag = candidate
            print(f'HIT : {flag}')
            setup()
            break
        else:
            print(f'{candidate} - {count}')
            if letter == WORDLIST[-1]:
                found = True

print(f'FLAG : {flag}')
