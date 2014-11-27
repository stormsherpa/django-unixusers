import crypt

from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.datastructures import SortedDict


class BaseUnixPasswordHasher(BasePasswordHasher):

    def encode(self, password, salt):
        assert password is not None
        assert salt and '$' not in salt
        crypted_pass = crypt.crypt(password, '${}${}'.format(self.password_hash_code, salt))
        return "{}{}".format(self.algorithm, crypted_pass)

    def verify(self, password, encoded):
        bare_encoded = encoded[len(self.algorithm):]
        crypted_pass = crypt.crypt(password, bare_encoded)
        return crypted_pass == bare_encoded

    def safe_summary(self, encoded):
        parts =  encoded.split('$', 3)
        algorithm, code, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        return SortedDict([
            ('algorithm', algorithm),
            ('salt', mask_hash(salt, show=2)),
            ('hash', mask_hash(hash)),
        ])

class MD5UnixPasswordHasher(BaseUnixPasswordHasher):
    password_hash_code = 1
    algorithm = "UnixMD5"

class Sha256UnixPasswordHasher(BaseUnixPasswordHasher):
    password_hash_code = 5
    algorithm = "UnixSha256"

class Sha512UnixPasswordHasher(BaseUnixPasswordHasher):
    password_hash_code = 6
    algorithm = "UnixSha512"
