# -*- coding: utf-8 -*-
from __future__ import absolute_import
import hashlib

def signature(secret_key, params, hash_secret=True):
    """
    Calculates money.mail.ru signature for the params dict.
    Pass hash_secret = True for signing outgoing requests
    and hash_secret=False for checking signatures of incoming requests.

    All params must be unicode because there is no way
    to find out what encoding byte string should be decoded from.
    """

    sorted_keys = sorted(key for key in params if key != 'signature')
    if hash_secret:
        key_bytes = secret_key.encode('cp1251')
        secret_hash = hashlib.sha1(key_bytes).hexdigest().encode('ascii')
    else:
        secret_hash = secret_key.encode('ascii')
    values = [params[key].encode('cp1251') for key in sorted_keys] + [secret_hash]
    sig_string = b"".join(values)
    return hashlib.sha1(sig_string).hexdigest()
