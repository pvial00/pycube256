# pycube256
A Linear Feedback Shift Register Stream Cipher
Python Implementation of the Cube256 Cipher

Supports binary data

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
