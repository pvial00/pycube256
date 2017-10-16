# pycube256 0.5.1

class Cube:
    def __init__(self, key, nonce="", sbox=[]):
        self.start_char = 0
        self.alphabet_size = 256
        self.size_factor = 3
        
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

class CubeHMAC:
    def __init__(self, nonce_length=8, algorithm="Cube"):
        self.algorithm = algorithm
        self.nonce_length = nonce_length

    def encrypt(self, data, key, nonce="", pack=True, compress=False):
        import hashlib, os, zlib
        if nonce == "":
            nonce = os.urandom(self.nonce_length)
        hash_key = hashlib.pbkdf2_hmac('sha256', key, 'Cube', 100000)
        if compress == True:
            if self.algorithm == "Cube":
                msg = Cube(key, nonce).encrypt(zlib.compress(data))
            elif self.algorithm == "CubeBlock":
                msg = CubeBlock(key, nonce).encrypt(zlib.compress(data))
        else:
            if self.algorithm == "Cube":
                msg = Cube(key, nonce).encrypt(data)
            elif self.algorithm == "CubeBlock":
                msg = CubeBlock(key, nonce).encrypt(data)
        digest = hashlib.sha256(hash_key+msg).digest()
        if pack == False:
            return msg, nonce, digest
        else:
            return nonce+digest+msg

    def decrypt(self, data, key, nonce="", digest="", pack=True, compress=False):
        import hashlib, zlib
        hash_key = hashlib.pbkdf2_hmac('sha256', key, 'Cube', 100000)
        if pack == False:
            if hashlib.sha256(hash_key+data).digest() == digest:
                if compress == True:
                    if self.algorithm == "Cube":
                        msg = zlib.decompress(Cube(key, nonce).decrypt(data))
                    elif self.algorithm == "CubeBlock":
                        msg = zlib.decompress(CubeBlock(key, nonce).decrypt(data))
                else:
                    if self.algorithm == "Cube":
                        msg = Cube(key, nonce).decrypt(data)
                    elif self.algorithm == "CubeBlock":
                        msg = CubeBlock(key, nonce).decrypt(data)
                return msg
            else:
                return ValueError('HMAC failed: Message has been tampered with!')
        else:
            nonce = data[:self.nonce_length]
            digest = data[self.nonce_length:self.nonce_length+32]
            msg = data[self.nonce_length+32:]
            if hashlib.sha256(hash_key+msg).digest() == digest:
                if compress == True:
                    msg = zlib.decompress(Cube(key, nonce).decrypt(msg))
                else:
                    msg = Cube(key, nonce).decrypt(msg)
                return msg
            else:
                return ValueError('HMAC failed: Message has been tampered with!')

class CubeHash:
    def __init__(self, mode=256):
        if mode == 128 or mode == 256 or mode == 512:
            self.mode = mode
        else:
            raise ValueError('Invalid hash mode')

    def hash(self, data):
        iv = chr(0) * (self.mode / 8)
        result = Cube(iv, data).encrypt(iv)
        return result

    def digest(self, data):
        result = self.hash(data)
        hash_result = result.encode('hex')
        return hash_result

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
                    self.entropy += chr(j)
                things[i], things[j] = things[j], things[i]
        return things

class CubeBlock:
    def __init__(self, key, nonce="", sbox=[]):
        self.block_size = 16
        self.start_char = 0
        self.alphabet_size = 256
        self.size_factor = 3
        
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
