from pycube256 import Cube
import sys, select, getpass, os, time, getopt
    
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
        data = sys.stdin.read()
    else:
        sys.exit(1)

    try:
        key = sys.argv[2]
    except IndexError as ier:
        key = getpass.getpass("Enter key: ")

    start = time.time()

    if mode == "encrypt":
        sys.stdout.write(Cube(key).encrypt(data))
    elif mode == "decrypt":
        sys.stdout.write(Cube(key).decrypt(data))

    end = time.time() - start
    bps = len(data) / end
    sys.stderr.write("Completed in "+str(end)+" seconds\n")
    sys.stderr.write(str(bps)+" bytes per second.\n")
