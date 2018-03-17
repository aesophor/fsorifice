from Crypto.Cipher import AES
from Crypto        import Random
from hashlib       import md5
import base64


class tcp_cipher(object):

    def __init__(self):
        self.BS    = 16
        self.pad   = lambda s: s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)
        self.unpad = lambda s : s[:-ord(s[len(s)-1:])]

    def encrypt(self, cleartext, password):
        cleartext = self.pad(cleartext)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(password, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(cleartext))

    def decrypt(self, ciphertext, password):
        ciphertext = base64.b64decode(ciphertext)
        iv = ciphertext[:16]
        cipher = AES.new(password, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(ciphertext[16:]))


class file_cipher(object):

    def __init__(self):
        pass

    def derive_key_and_iv(self, password, salt, key_length, iv_length):
        d = d_i = ''
        while len(d) < key_length + iv_length:
            d_i = md5(d_i + password + salt).digest()
            d += d_i
        return d[:key_length], d[key_length:key_length+iv_length]

    def encrypt(self, in_file, out_file, password, key_length=32):
        # remember to re-encode the password.
        password = str(password)

        bs = AES.block_size
        salt = Random.new().read(bs - len('Salted__'))
        key, iv = self.derive_key_and_iv(password, salt, key_length, bs)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        out_file.write('Salted__' + salt)
        finished = False
        while not finished:
            chunk = in_file.read(1024 * bs)
            if len(chunk) == 0 or len(chunk) % bs != 0:
                padding_length = (bs - len(chunk) % bs) or bs
                chunk += padding_length * chr(padding_length)
                finished = True
            out_file.write(cipher.encrypt(chunk))

    def decrypt(self, in_file, out_file, password, key_length=32):
        # remember to re-encode the password.
        password = str(password)

        bs = AES.block_size
        salt = in_file.read(bs)[len('Salted__'):]
        key, iv = self.derive_key_and_iv(password, salt, key_length, bs)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        next_chunk = ''
        finished = False
        while not finished:
            chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
            if len(next_chunk) == 0:
                padding_length = ord(chunk[-1])
                chunk = chunk[:-padding_length]
                finished = True
            out_file.write(chunk)

    def enc_file(self, in_filename, out_filename, password):
        with open(in_filename, 'rb') as in_file, open(out_filename, 'wb') as out_file:
            self.encrypt(in_file, out_file, password)

    def dec_file(self, in_filename, out_filename, password):
        with open(in_filename, 'rb') as in_file, open(out_filename, 'wb') as out_file:
            self.decrypt(in_file, out_file, password)
