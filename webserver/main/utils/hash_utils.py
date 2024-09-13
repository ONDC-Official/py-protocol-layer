import hashlib


def get_md5_hash(big_string):
    md5_hash = hashlib.md5(big_string.encode('utf-8')).hexdigest()
    return md5_hash
