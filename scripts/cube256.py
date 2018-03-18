from pycube256 import Cube, CubeRandom, CubeKDF
import sys, select, getpass, os, time, getopt

try:
    mode = sys.argv[1]
except IndexError as ier:
    print "Error: Did you forget encrypt/decrypt?"
    sys.exit(1)

input_filename = sys.argv[2]
output_filename = sys.argv[3]

try:
    infile = open(input_filename, "r")
except IOError as ier:
    print "Input file not found."
    sys.exit(1)

try:
    outfile = open(output_filename, "w")
except IOError as ier:
    print "Output file not found."
    sys.exit(1)

try:
    key = sys.argv[4]
except IndexError as ier:
    key = getpass.getpass("Enter key: ")

# 128 bit key size
key = CubeKDF().genkey(key, length=16)

start = time.time()
data = infile.read()
infile.close()

if mode == "encrypt":
    nonce = os.urandom(16)
    c = Cube(key, nonce).encrypt(data)
    outfile.write(nonce+c)
elif mode == "decrypt":
    nonce = data[:16]
    msg = data[16:len(data) -1]
    plain_text = Cube(key, nonce).decrypt(msg)
    outfile.write(plain_text)
outfile.close()

end = time.time() - start
bps = len(data) / end
sys.stdout.write("Completed in "+str(end)+" seconds\n")
sys.stdout.write(str(bps)+" bytes per second.\n")
