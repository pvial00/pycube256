# pycube256
A Linear Feedback Shift Register Stream Cipher
Python Implementation of the Cube256 Cipher

Supports binary data

pycube256 also includes a random number generator and hash function CubeRandom() and CubeHash()

# Usage:
>>> from pycube256 import Cube
>>> Cube("Test").encrypt("Welcome!")
'pe8LZ0u('
>>> Cube("Test").decrypt("pe8LZ0u(")
'Welcome!'

# Passing a  nonce:
>>> from pycube256 import Cube
>>> Cube("Test", "NONCE").encrypt("Welcome!")
>>> Cube("Test", "NONCE").decrypt("pe8LZ0u(")

# Standalone script usage:
scripts/cube256.py <encrypt/decrypt>
cat filename | python cube256.py key > file

# CubeHMAC:
Signature checking tamper detection  
(optional compression support)  

from pycube256 import CubeHMAC
pack = CubeHMAC().encrypt(msg, key)  
plain = CubeHMAC().decrypt(pack, key)  

Without packing  
hmac, nonce, dig = CubeHMAC().encrypt(msg, key, pack=False)  
plain = CubeHMAC().decrypt(hmac, key, nonce, dig, pack=False)  

With compression  
pack = CubeHMAC().encrypt(msg, key, compress=True)  
plain = CubeHMAC().decrypt(pack, key, compress=True)  

# CubeHash:
from pycube256 import CubeHash
stuff = "somethingtodo"
print CubeHash().digest(stuff)
b6ce700230738258646e0f302e84ccc4c8e08ac32c9f8918506f0231fcfeed22

# CubeRandom:
(Generates random value from 0 to 255 or chooses from or shuffles up to 256 items)  
from pycube256 import CubeRandom  
print CubeRandom().random()  
?

print CubeRandom().randrange(32, 122, 16)  
EX^`%A$#=^3x"[F,

print CubeRandom().randint(0, 10)  
4

things = [ 'apples', 'oranges', 'peach', 'pear', 'grapes', 'bananas']  
print CubeRandom().shuffle(things)  
['peach', 'apples', 'oranges', 'pear', 'bananas', 'grapes']  

things = ['peach', 'apples', 'oranges', 'pear', 'bananas', 'grapes']  
print CubeRandom().choice(things)  
oranges  

# CubeBlock:  
Experimental Block cipher based on Cube  

CubeBlock("key").encrypt(data)
CubeBlock("key", "nonce").decrypt(data) 
