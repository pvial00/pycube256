from pycube256 import Cube
import sys, select, getpass, os

if select.select([sys.stdin,],[],[],0.0)[0]:
    words = sys.stdin.read()
    words = words.replace('\n', '')
else:
    words = raw_input("Enter text to cipher: ")

try:
    mode = sys.argv[1]
except IndexError as ier:
    print "Error: Did you forget encrypt/decrypt?"
    sys.exit(1)

try:
    key = sys.argv[2]
except IndexError as ier:
    key = getpass.getpass("Enter key: ")

if mode == "encrypt":
    print Cube(key).encrypt(words)
elif mode == "decrypt":
    print Cube(key).decrypt(words)
