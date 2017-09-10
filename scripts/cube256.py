from pycube256 import Cube
import sys, select, getpass, os
    
try:
    mode = sys.argv[1]
except IndexError as ier:
    print "Error: Did you forget encrypt/decrypt?"
    sys.exit(1)

if mode == "selftest":
    cube = Cube("ABCDEFGHIJKLMNOP")
    cube.selftest()
else:

    if select.select([sys.stdin,],[],[],0.0)[0]:
        words = sys.stdin.read()
        lastbyte = words[len(words) - 1:len(words)]
        if lastbyte == chr(10):
            words = words[:len(words) - 1]
    else:
        words = raw_input("Enter text to cipher: ")

    try:
        key = sys.argv[2]
    except IndexError as ier:
        key = getpass.getpass("Enter key: ")

    if mode == "encrypt":
        print Cube(key).encrypt(words)
    elif mode == "decrypt":
        print Cube(key).decrypt(words)
