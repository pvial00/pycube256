# pycube256 0.5.5

class Cube:
    def __init__(self, key, nonce="", sbox=[]):
        self.start_char = 0
        self.alphabet_size = 256
        self.size_factor = 3
        self.key = []
        for byte in key:
            self.key.append(ord(byte))

        if len(sbox) == self.size_factor:
            self.sbox = sbox
        else:
            self.sbox = self.gen_cube(self.size_factor, self.size_factor, self.alphabet_size)

        self.key_cube(self.key)
        if nonce != "":
            noncelist = []
            for byte in nonce:
                noncelist.append(ord(byte))
            self.key_cube(noncelist)

    # Generate the initial permutation of the Cube S-Box
    def gen_cube(self, depth, width, length):
        sbox = []
        for z in range(0,depth):
            section_list = []
            for y in range(0,width):
                alphabet = []
                for x in range(0,length):
                    alphabet.append(x)
                for mod in range(0,y):
                    shift = alphabet.pop(0)
                    alphabet.append(shift)
                    shift = alphabet.pop(2)
                    alphabet.insert(127,shift)
                section_list.append(alphabet)
            sbox.append(section_list)
        return sbox

    # Apply the key to the Cube to create the inital permutation of Cube
    def key_cube(self, key):
        for section in self.sbox:
            for char in key:
                for alphabet in section:
                    key_sub = alphabet.pop(char)
                    alphabet.append(key_sub)
                    for y in range(0,char):
                        if y % 2 == 0:
                            shuffle = alphabet.pop(0)
                            alphabet.append(shuffle)
                            shuffle = alphabet.pop(2)
                            alphabet.insert(127,shuffle)
        for char in key:
            sized_pos = char % self.size_factor
            for x in range(char):
                section = self.sbox.pop(sized_pos)
                self.sbox.append(section)
   
    # Substitute a new round key
    def key_scheduler(self, key):
        sub_key = []
        for element in key:
            sized_pos = element % self.size_factor
            section = self.sbox[sized_pos]
            sub_alpha = section[sized_pos]
            sub = sub_alpha.pop(element)
            sub_alpha.append(sub)
            sub_key.append(sub)
        return sub_key

    # Morphing round to permute the Cube S-Box into a new configuration
    def morph_cube(self, counter, sub_key):
        mod_value = counter % self.alphabet_size
        for section in self.sbox:
            for key_element in sub_key:
                for alphabet in section:
                    alphabet[mod_value], alphabet[key_element] = alphabet[key_element], alphabet[mod_value]
            section_shift = self.sbox.pop(key_element % self.size_factor)
            self.sbox.append(section_shift)

    # Substitute data through all alphabets
    def encrypt(self, data):
        cipher_text = ""
        sub_key = self.key
        for counter, letter in enumerate(data):
            sub = ord(letter)
            for section in self.sbox:
                for alphabet in section:
                    sub_pos = sub
                    sub = alphabet[sub_pos]
                    shift = alphabet.pop(0)
                    alphabet.append(shift)
            sub_key = self.key_scheduler(sub_key)
            self.morph_cube(counter, sub_key)
            cipher_text += chr(sub)
        return cipher_text

    # Substitute data through all alphabets
    def decrypt(self, data):
        plain_text = ""
        sub_key = self.key
        for counter, letter in enumerate(data):
            sub = ord(letter)
            for section in reversed(self.sbox):
                for alphabet in reversed(section):
                    sub = alphabet.index(sub)
                    shift = alphabet.pop(0)
                    alphabet.append(shift)
            sub_key = self.key_scheduler(sub_key)
            self.morph_cube(counter, sub_key)
            plain_text += chr(sub)
        return plain_text

    # Perform a self test to ensure all initial alphabets are unique
    def uniquetest(self):
        import hashlib
        hashlist = []
        buf =""
        result = True
        for section in self.sbox:
            for alphabet in section:
                for char in alphabet:
                    buf += chr(char)
                entry = hashlib.sha224(buf).digest()
                if entry in hashlist:
                    print "Failure: Entry " + entry + " is not unique!"
                    result = False
                else:
                    hashlist.append(entry)
        if result == True:
            print "Self test passed"
        else:
            print "Self test failed"
        return result

class CubeTest:
    def selftest(self):
        testdata = "Cube256 Stream Cipher Test Data set #1"
        testnonce = "12345678"
        testkey = "ABCDEFGHIJKLNOP"
        result = Cube(testkey, testnonce).encrypt(testdata)
        if result.encode('hex') == "cc0026313329eee3a8a25c90f9e6dbde39cdb4ad6e2f236864f4593283c609864cfb2751ecba":
            return True
        else:
            return False

class CubeHMAC:
    def __init__(self, nonce_length=8):
        self.nonce_length = nonce_length
        self.digest_length = 32

    def encrypt(self, data, key, nonce="", aad="", pack=True, compress=False, salt='%39xS01(#Ef78a41aB2$'):
        import hashlib, os, zlib
        if nonce == "":
            nonce = CubeRandom().random(self.nonce_length)
        hash_key = hashlib.pbkdf2_hmac('sha256', key, salt, 100001)
        if compress == True:
            msg = Cube(key, nonce).encrypt(zlib.compress(data))
        else:
            msg = Cube(key, nonce).encrypt(data)
        digest1 = hashlib.sha256(key+aad+nonce+msg).digest()
        digest = hashlib.sha256(hash_key+digest1).digest()
        if pack == False:
            return aad, nonce, digest, msg
        else:
            return aad+nonce+digest+msg

    def decrypt(self, data, key, nonce="", aad="", aadlen=0, digest="", pack=True, compress=False, salt='%39xS01(#Ef78a41aB2$'):
        import hashlib, zlib
        hash_key = hashlib.pbkdf2_hmac('sha256', key, salt, 100001)
        if pack == False:
            digest1 = hashlib.sha256(key+aad+nonce+data).digest()
            if hashlib.sha256(hash_key+digest1).digest() == digest:
                if compress == True:
                    return zlib.decompress(Cube(key, nonce).decrypt(data))
                else:
                    return Cube(key, nonce).decrypt(data)
            else:
                raise ValueError('HMAC failed: Message has been tampered with!')
        else:
            aad = data[:aadlen]
            nonce = data[aadlen:aadlen+self.nonce_length]
            digest = data[aadlen+self.nonce_length:aadlen+self.nonce_length+self.digest_length]
            msg = data[aadlen+self.nonce_length+self.digest_length:]
            digest1 = hashlib.sha256(key+aad+nonce+msg).digest()
            if hashlib.sha256(hash_key+digest1).digest() == digest:
                if compress == True:
                    return zlib.decompress(Cube(key, nonce).decrypt(msg))
                else:
                    return Cube(key, nonce).decrypt(msg)
            else:
                raise ValueError('HMAC failed: Message has been tampered with!')

class CubeSum:
    def __init__(self, mode=16):
        self.mode = mode

    def hash(self, data, key=""):
        if key == "":
            iv = chr(0) * self.mode
            return Cube(data, iv).encrypt(iv)
        else:
            return Cube(data, key).encrypt(key)
        return result

    def digest(self, data, key=""):
        self.hash(data, key)
        return result.encode('hex')

class CubeRandom:
    def __init__(self, iv=16):
        import os
        self.entropy = os.urandom(iv)

    def random(self, num=1):
        iv = chr(0) * num
        return  Cube(self.entropy).encrypt(iv)

    def choice(self, things):
        num = len(things)
        result = ord(self.random(1)) % num
        return things[result]

    def randrange(self, min, max, num=1):
        randbytes = self.random(num)
        result = ""
        for byte in randbytes:
            char = chr(ord(byte) % (max - min + 1) + min)
            result += char
        return result
    
    def randint(self, min=0, max=255):
        randbyte = self.random(1)
        result = ord(randbyte) % (max - min + 1) + min
        return result

    def shuffle(self, things):
        num = len(things)
        import array
        from collections import deque
        if type(things) is list or type(things) is array.array or type(things) is deque:
            for i in reversed(range(num)):
                j = num+1
                while j > i:
                    j = self.randint(0, num-1)
                    self.entropy = self.entropy[:16] + chr(j)
                things[i], things[j] = things[j], things[i]
        return things

class CubeBlock:
    def __init__(self, key, nonce="", sbox=[], padding=True):
        self.block_size = 16
        self.start_char = 0
        self.alphabet_size = 256
        self.size_factor = 3
        self.padding = padding
        
        if len(sbox) == self.size_factor:
            self.sbox = sbox
        else:
            self.sbox = self.gen_cube(self.size_factor, self.size_factor, self.alphabet_size)

        self.key_init(key)
        if nonce != "":
            noncelist = []
            for char in nonce:
                noncelist.append(ord(char))
            self.key_cube(noncelist)
    
    def key_init(self, initkey):
        key = []
        for char in initkey:
            key.append(ord(char))
        self.load_key(key)
        self.key_cube(key)
        
    # Generate the initial permutation of the Cube S-Box
    def gen_cube(self, depth, width, length):
        sbox = []
        for z in range(0,depth):
            section_list = []
            for y in range(0,width):
                alphabet = []
                for x in range(0,length):
                    alphabet.append(x)
                for mod in range(0,y):
                    shift = alphabet.pop(0)
                    alphabet.append(shift)
                    shift = alphabet.pop(2)
                    alphabet.insert(127,shift)
                section_list.append(alphabet)
            sbox.append(section_list)
        return sbox

    # Apply the key to the Cube to create the inital permutation of Cube
    def key_cube(self, key):
        for section in self.sbox:
            for char in key:
                for alphabet in section:
                    key_sub = alphabet.pop(char)
                    alphabet.append(key_sub)
                    for y in range(0,char):
                        if y % 2 == 0:
                            shuffle = alphabet.pop(0)
                            alphabet.append(shuffle)
                            shuffle = alphabet.pop(2)
                            alphabet.insert(127,shuffle)
        for char in key:
            sized_pos = char % self.size_factor
            for x in range(char):
                section = self.sbox.pop(sized_pos)
                self.sbox.append(section)
    
    def load_key(self, skey):
        self.key_list = []
        self.key = skey
        for element in self.key:
            self.key_list.append(element)

    # Substitute a new round key
    def key_scheduler(self, key):
        sub_key = []
        for element in key:
            sized_pos = element % self.size_factor
            section = self.sbox[sized_pos]
            sub_alpha = section[sized_pos]
            sub = sub_alpha.pop(element)
            sub_alpha.append(sub)
            sub_key.append(sub)
        self.load_key(sub_key)
        return sub_key

    # Morphing round to permute the Cube S-Box into a new configuration
    def morph_cube(self, counter, sub_key):
        mod_value = counter % self.alphabet_size
        for section in self.sbox:
            for key_element in sub_key:
                for alphabet in section:
                    alphabet[mod_value], alphabet[key_element] = alphabet[key_element], alphabet[mod_value]
            section_shift = self.sbox.pop(key_element % self.size_factor)
            self.sbox.append(section_shift)

    # Substitute data through all alphabets
    def encrypt(self, data):
        cipher_text = ""
        sub_key = self.key
        num_blocks = len(data) / self.block_size
        extra_bytes = len(data) % self.block_size
        if extra_bytes != 0:
            num_blocks += 1
        c = 0
        blocks = []
        for x in range(num_blocks):
            blocks.append(data[c:c+self.block_size])
            c+=self.block_size

        for block_counter, block in enumerate(blocks):
            if block_counter == num_blocks - 1:
                # If padding is enabled the last block is padded
                if self.padding == True:
                    if len(block) < self.block_size:
                        pad_byte = self.block_size - len(block)
                        padding = chr(pad_byte) * (pad_byte)
                        block += padding

            for counter, byte in enumerate(block):
                sub = ord(byte)
                for section in self.sbox:
                    for alphabet in section:
                        sub_pos = sub
                        sub = alphabet[sub_pos]
                        shift = alphabet.pop(0)
                        alphabet.append(shift)
                cipher_text += chr(sub)
            sub_key = self.key_scheduler(sub_key)
            self.morph_cube(counter, sub_key)
        return cipher_text

    # Substitute data through all alphabets
    def decrypt(self, data):
        plain_text = ""
        sub_key = self.key
        num_blocks = len(data) / self.block_size
        c = 0
        blocks = []
        for x in range(num_blocks):
            blocks.append(data[c:c+self.block_size])
            c+=self.block_size

        for block_counter, block in enumerate(blocks):
            for counter, byte in enumerate(block):
                sub = ord(byte)
                for section in reversed(self.sbox):
                    for alphabet in reversed(section):
                        sub = alphabet.index(sub)
                        shift = alphabet.pop(0)
                        alphabet.append(shift)
                plain_text += chr(sub)
            # If padding is enabled the last block is unpadded
            if self.padding == True:
                if block_counter == (num_blocks - 1):
                    pad_block = plain_text[len(plain_text) - (self.block_size):]
                    pad_count = ord(pad_block[self.block_size - 1])
                    true_pad_count = 0
                    for x in reversed(range(len(pad_block))):
                        if ord(pad_block[x]) == pad_count:
                            true_pad_count += 1
                    if pad_count == true_pad_count:
                        plain_text = plain_text[:len(plain_text) - pad_count]

            sub_key = self.key_scheduler(sub_key)
            self.morph_cube(counter, sub_key)
        return plain_text

    # Perform a self test to ensure all initial alphabets are unique
    def selftest(self):
        import hashlib
        hashlist = []
        buf =""
        result = True
        for section in self.sbox:
            for alphabet in section:
                for char in alphabet:
                    buf += chr(char)
                entry = hashlib.sha224(buf).digest()
                if entry in hashlist:
                    print "Failure: Entry " + entry + " is not unique!"
                    result = False
                else:
                    hashlist.append(entry)
        if result == True:
            print "Self test passed"
        else:
            print "Self test failed"
        return result

class CubeSharedKey:
    def __init__(self, keys=None, num_keys=2, keylength=16):
        if keys == None:
            keys = CubeKeys().genkeys(num_keys, keylength)
        self.keys = list(keys)
        self.master_key = self.xor(keys.pop(0), keys.pop(0))
        for key in keys:
            self.master_key = self.xor(self.master_key, key)

    def xor(self, key1, key2):
        new_key = ""
        for x in range(len(key1)):
            new_key+= chr(ord(key1[x]) ^ ord(key2[x]))
        return new_key

    def encrypt(self, data):
        return CubeHMAC().encrypt(data, self.master_key)

    def decrypt(self, data):
        return CubeHMAC().decrypt(data, self.master_key)

class CubeKDF:
    def genkey(self, key, iterations=10, length=16):
        h = key
        key = CubeSum(mode=length).hash(key)
        for x in range(iterations):
            h = CubeSum(mode=length).hash(h, key)
        return h

class CubeKeys:
    def genkeys(self, num_keys=1, keylength=16):
        keys = []
        for x in range(num_keys):
            keys.append(CubeRandom().random(keylength))
        return keys

class CubeKeyWrap:
    def __init__(self):
        self.keylength = 16

    def wrapkey(self, key, session_key):
        return Cube(key).encrypt(session_key)

    def unwrapkey(self, key, hidden_key):
        return Cube(key).decrypt(hidden_key)

    def encrypt(self, data, key):
        skey = CubeKeys().genkeys(1, self.keylength)
        session_key = skey.pop()
        cipher_text = CubeHMAC().encrypt(data, session_key)
        hidden_key = self.wrapkey(key, session_key)
        return hidden_key+cipher_text

    def decrypt(self, data, key):
        hidden_key = data[:self.keylength]
        session_key = self.unwrapkey(key, hidden_key)
        cipher_text = data[self.keylength:]
        return CubeHMAC().decrypt(cipher_text, session_key)

class CubePIN:
    def __init__(self, length=4):
        self.length = length
        self.min = 0
        self.max = 9

    def generate(self, num=1):
        pin = ""
        for x in range(self.length):
            pin += str(CubeRandom().randint(self.min, self.max))
        return pin
