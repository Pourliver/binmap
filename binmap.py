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
# handle errors

parser = argparse.ArgumentParser(description='ADD NAME')
parser.add_argument('file', metavar='file', help='The file to execute')
parser.add_argument('--x64', action='store_true', help='Toggles the x64 mode')
parser.add_argument('-w', '--wordlist', default=string.printable, help='The list of caracters to use (minimum 2 caracters)')
parser.add_argument('-l', '--length', default=0, type=int, help='The length of the password')
config = configparser.ConfigParser()
args = parser.parse_args()
BINMAP_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = f'{BINMAP_PATH}/config.ini'
WORDLIST = args.wordlist
FILE = args.file
PAD_LEN = args.length
MIN_COUNT = 0
flag = ''

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


def setup(word1, word2):
    case1 = pin(word1)
    case2 = pin(word2)

    return min([case1, case2])

def bruteforce(flag, wordlist, pad_len, min_count):
    for letter in wordlist:
        candidate = (flag + letter).ljust(pad_len, wordlist[0])
        print(candidate)
        count = pin(candidate)

        if count > min_count:
            # Update flag
            flag = flag + letter
            print(f'HIT : {flag}')
            return flag
        else:
            print(f'{candidate} - {count}')
    # Flag hasn't changed
    return flag


def main(wordlist, pad_len, min_count):
    found = False
    flag = ''

    while not found:
        word1 =(flag + wordlist[0]).ljust(pad_len, wordlist[0])
        word2 =(flag + wordlist[1]).ljust(pad_len, wordlist[0])
        min_count = setup(word1, word2)
        new_flag = bruteforce(flag, wordlist, pad_len, min_count)
        
        # If flag has changed, keep going
        if new_flag != flag:
            flag = new_flag
        else:
            found = True
    
    print(f'FLAG : {flag}')

if __name__ == "__main__":
    main(WORDLIST, PAD_LEN, MIN_COUNT)