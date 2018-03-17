from Crypto.PublicKey import RSA
from Crypto           import Random
import cPickle

class key_cipher(object):

    def __init__(self):
        pass

    def generate_rsa_keypair(self):
        # randomly generate a keypair for current session.
        self.random_gen = Random.new().read
        self.rsakey     = RSA.generate(1024, self.random_gen)
        self.pubkey     = self.rsakey.publickey()
        return self.pubkey

    def generate_aes(self):
        return Random.new().read(32)

    def encrypt(self, pubkey, cleartext):
        return pubkey.encrypt(cleartext, 32)[0]

    def decrypt(self, ciphertext):
        return self.rsakey.decrypt(ciphertext)
