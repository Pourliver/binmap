#/bin/python3
from multiprocessing.pool import ThreadPool
from itertools import repeat, chain, islice
import concurrent.futures
import subprocess
import configparser
import argparse
import os.path
import string
import sys
import re
import time

# TODO
# wrap under a main function
# make everything more readable
# make a great description
# handle errors

parser = argparse.ArgumentParser(description='ADD NAME')

# Required positional argument
parser.add_argument('file', metavar='file', help='The file to execute')

# Optional argument
parser.add_argument('--x64', action='store_true', help='Toggles the x64 mode (manual for now)')
parser.add_argument('-w', '--wordlist', default=string.printable, help='The list of caracters to use (minimum 2 caracters)')
parser.add_argument('-l', '--length', default=0, type=int, help='The length of the password, if known. May be needed to pass checks inside the executable')
config = configparser.ConfigParser()
args = parser.parse_args()

BINMAP_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = f'{BINMAP_PATH}/config.ini'
WORDLIST = args.wordlist
FILE = args.file
PAD_LEN = args.length

if (os.path.exists(CONFIG_PATH)):
    config.read(CONFIG_PATH)
    PIN_FOLDER = config['DEFAULT']['pin_folder']
else:
    PIN_FOLDER = input('Enter your pin install path [/opt/pin] : ') or "/opt/pin"
    config['DEFAULT'] = {'pin_folder' : PIN_FOLDER}
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)

if args.x64:
    SO_PATH = f"{PIN_FOLDER}/obj-intel64/inscount0.so"
else:
    SO_PATH = f"{PIN_FOLDER}/obj-ia32/inscount0.so"

if args.wordlist:
    if len(args.wordlist) < 2:
        parser.error("A wordlist needs a least 2 caracters.")
    WORDLIST = args.wordlist    
else:
    WORDLIST = string.printable

def pin_wrap(pair):
    return (pin(pair[0]), pair[1])

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


def get_minimum_count(flag, letter1, letter2, pad_len):
    word1 =(flag + letter1).ljust(pad_len, letter1)
    word2 =(flag + letter2).ljust(pad_len, letter1)
    case1 = pin(word1)
    case2 = pin(word2)

    return min([case1, case2])

def bruteforce(flag, wordlist, pad_len, min_count):

    # Generate possibilites, (candidate, letter) pair
    candidates = []

    for letter in wordlist:
        candidate = (flag + letter).ljust(pad_len, wordlist[0])
        candidates.append((candidate, letter))

    pool = ThreadPool(10)
    for count, letter in pool.imap(pin_wrap, candidates):
        print("[+]", letter)

        if count > min_count:
            # Update flag
            flag = flag + letter
            break

    pool.terminate()
    pool.join()

    return flag

def generate_with_padding(tobeiterated, n, pad = None):
    return islice(chain(tobeiterated, repeat(pad)), n)

def main(wordlist, pad_len):
    found = False
    flag = ''

    start = time.time()
    while not found:
        print("[+] Current flag :", flag)

        # Get minimum possible instruction count
        min_count = get_minimum_count(flag, wordlist[0], wordlist[1], pad_len)

        new_flag = bruteforce(flag, wordlist, pad_len, min_count)
        
        # If flag has changed, keep going
        if new_flag != flag:
            flag = new_flag
        else:
            found = True

    end = time.time()
    print("[+] Elapsed time :", end-start)
    print("[+] FLAG :", flag)

if __name__ == "__main__":

    main(WORDLIST, PAD_LEN)