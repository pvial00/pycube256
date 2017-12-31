from pycube256 import CubeHMAC, CubeKDF, CubeRandom
import sys, select, getpass, os, time, getopt, subprocess
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random

def gen_rsa_keypair(bits, filename):
	random_gen = Random.new().read
	key = RSA.generate(bits, random_gen)
	private_key = key.exportKey()
	public_key = key.publickey().exportKey()
	priv_keyfile = filename + ".private"
	pub_keyfile = filename + ".public"
	priv_key_fd = open(priv_keyfile, "w")
	pub_key_fd = open(pub_keyfile, "w")
	priv_key_fd.write(private_key)
	pub_key_fd.write(public_key)
	priv_key_fd.close()
	pub_key_fd.close()

def import_priv_key(filename):
	priv_keyfile = filename
	priv_key_fd = open(priv_keyfile, "r")
	private_key = RSA.importKey(priv_key_fd.read())
	priv_key_fd.close()
	return private_key

def import_pub_key(filename):
	pub_keyfile = filename
	pub_key_fd = open(pub_keyfile, "r")
	public_key = RSA.importKey(pub_key_fd.read())
	pub_key_fd.close()
	return public_key

def rsa_encrypt(data, public_key):
	cipher = PKCS1_OAEP.new(public_key)
	cipher_text = cipher.encrypt(data)
	return cipher_text

def rsa_decrypt(data, private_key):
	cipher = PKCS1_OAEP.new(private_key)
	plain_text = cipher.decrypt(data)
	return plain_text

try:
    mode = sys.argv[1]
except IndexError as ier:
    print "Error: Did you forget encrypt/decrypt/gen?"
    sys.exit(1)

if mode == "gen":
    keybits = int(raw_input("Enter RSA key length in bits: "))
    filename = raw_input("Enter filename prefix for keys: ")
    gen_rsa_keypair(keybits, filename)
    sys.exit(0)

input_filename = sys.argv[2]
output_filename = sys.argv[3]

try:
    outfile = open(output_filename, "w")
except IOError as ier:
    print "Output file not found."
    sys.exit(1)

start = time.time()

if mode == "encrypt":
    try:
        infile = open(input_filename, "r")
    except IOError as ier:
        print "Input file not found."
        sys.exit(1)
    data = infile.read()
    infile.close()
    pubkey = raw_input("Enter public key filename: ")
    pk = import_pub_key(pubkey)
    session_key = CubeRandom().random(16)
    sessionpkg = rsa_encrypt(session_key, pk)
    sfd = open(output_filename+".pkg", "w")
    sfd.write(sessionpkg)
    sfd.close()
    outfile.write(CubeHMAC().encrypt(data, session_key, compress=False))
    outfile.close()
    os.system("tar -cvf "+output_filename+".tar"+" "+output_filename+" "+output_filename+".pkg")
    os.system("rm "+output_filename)
    os.system("rm "+output_filename+".pkg")
elif mode == "decrypt":
    privkey = raw_input("Enter private key filename: ")
    sk = import_priv_key(privkey)
    try:
        pkgfile = open(input_filename+".pkg", "r")
        pkg = pkgfile.read()
    except IOError as ier:
        print "Couldn't open pkg file."
        sys.exit(1)
    os.system("tar -xvf "+input_filename+".tar")
    pkgfile.close()
    session_key = rsa_decrypt(pkg, sk)
    try:
        datafile = open(input_filename, "r")
        data = datafile.read()
    except IOError as ier:
        print "Couldn't open data file."
        sys.exit(1)
    datafile.close()
    plain_text = CubeHMAC().decrypt(data, session_key, compress=False)
    outfile.write(plain_text)
    outfile.close()

end = time.time() - start
bps = len(data) / end
sys.stdout.write("Completed in "+str(end)+" seconds\n")
sys.stdout.write(str(bps)+" bytes per second.\n")
