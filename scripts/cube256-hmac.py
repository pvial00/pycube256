from pycube256 import Cube, CubeHMAC
import sys, select, getpass, os, time, getopt, hashlib
    
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
    passkey = sys.argv[4]
except IndexError as ier:
    passkey = getpass.getpass("Enter key: ")

key = hashlib.pbkdf2_hmac('sha256', passkey, '~03f%O4nI2)Vk@5Gy[31q', 100000)

start = time.time()
data = infile.read()
infile.close()

if mode == "encrypt":
    outfile.write(CubeHMAC().encrypt(data, key, compress=True))
elif mode == "decrypt":
    outfile.write(CubeHMAC().decrypt(data, key, compress=True))
outfile.close()

end = time.time() - start
bps = len(data) / end
sys.stdout.write("Completed in "+str(end)+" seconds\n")
sys.stdout.write(str(bps)+" bytes per second.\n")
