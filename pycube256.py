import hashlib
# pycube256 0.1.1

class Cube:
    def __init__(self, key, nonce=""):
        self.key_list = []
        self.key = ""
        self.master_list = []
        self.alphabet_dict = {}
        self.alphabet_dict_rev = {}
        self.start_char = 0
        self.alphabet_size = 256
        self.size_factor = 3

        def gen_cube(depth, width, length):
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
                self.master_list.append(section_list)

        gen_cube(self.size_factor, self.size_factor, self.alphabet_size)
        self.init(key)
        if nonce != "":
            noncelist = []
            for char in nonce:
                noncelist.append(ord(char))
            self.key_cube(noncelist)

    def key_cube(self, key):
        for section in self.master_list:
            for char in key:
                #sized_pos = char % self.size_factor
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
                section = self.master_list.pop(sized_pos)
                newpos = (sized_pos + x) % self.size_factor
                self.master_list.insert(newpos,section)

    def load_key(self, skey):
        self.key = skey
        for element in self.key:
            self.key_list.append(element)

    def key_scheduler(self, key):
        sub_key = []
        for element in key:
            sized_pos = element % self.size_factor
            section = self.master_list.pop(sized_pos)
            sub_alpha = section.pop(sized_pos)
            sub = sub_alpha.pop(element)
            sub_alpha.append(sub)
            section.insert(element,sub_alpha)
            self.master_list.insert(sized_pos,section)
            sub_key.append(sub)
        self.load_key(sub_key)
        return sub_key
    
    def init(self, initkey):
        key = []
        for char in initkey:
            key.append(ord(char))
        self.load_key(key)
        self.key_cube(key)

    def morph_cube(self, counter, sub_key):
        mod_value = counter % self.size_factor
        for key_element in sub_key:
            shift_value = (mod_value + key_element) % self.size_factor
            for section in self.master_list:
                for alphabet in section:
                    shift = alphabet.pop(mod_value)
                    alphabet.insert(shift_value,shift)
            section_shift = self.master_list.pop(key_element % self.size_factor)
            self.master_list.append(section_shift)

    def encrypt(self, words):
        cipher_text = ""
        sub_key = self.key
        for counter, letter in enumerate(words):
            sub = ord(letter)
            for section in self.master_list:
                for alphabet in section:
                    sub_pos = sub
                    sub = alphabet.pop(sub_pos)
                    alphabet.insert(sub_pos,sub)
                    shift = alphabet.pop(0)
                    alphabet.append(shift)
            sub_key = self.key_scheduler(sub_key)
            self.morph_cube(counter, sub_key)
            cipher_text += chr(sub)
        return cipher_text

    def decrypt(self, words):
        plain_text = ""
        sub_key = self.key
        for counter, letter in enumerate(words):
            sub = ord(letter)
            for section in reversed(self.master_list):
                for alphabet in reversed(section):
                    sub = alphabet.index(sub)
                    shift = alphabet.pop(0)
                    alphabet.append(shift)
            sub_key = self.key_scheduler(sub_key)
            self.morph_cube(counter, sub_key)
            plain_text += chr(sub)
        return plain_text

    def selftest(self):
        hashlist = []
        buf =""
        result = True
        for section in self.master_list:
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
