# -*- coding: utf-8 -*-
from __future__ import division


# For hash functions see http://www.partow.net/programming/hashfunctions/index.html
# Author Arash Partow, CPL http://www.opensource.org/licenses/cpl1.0.php
def fnv_hash(key):
    fnv_prime = 0x811C9DC5
    result = 0
    for i in range(len(key)):
        result *= fnv_prime
        result ^= ord(key[i])
    return result


def ap_hash(key):
    result = 0xAAAAAAAA
    for i in range(len(key)):
        if (i & 1) == 0:
            result ^= ((result << 7) ^ ord(key[i]) * (result >> 3))
        else:
            result ^= (~((result << 11) + ord(key[i]) ^ (result >> 5)))
    return result


class BloomFilter(object):
    MAX_OFFSET = 4294967294  # 2^32-2 (~512 Mb)
    DEFAULT_OFFSET = MAX_OFFSET
    DEFAULT_HASHES = 8

    def __init__(self, connection, key_prefix, num_bits=DEFAULT_OFFSET, num_hashes=DEFAULT_HASHES):
        self.connection = connection
        self.n = num_bits
        self.k = num_hashes
        self.keys = self.calculate_keys(key_prefix)

    def calculate_keys(self, key_prefix):
        div = self.n // self.MAX_OFFSET
        rem = self.n % self.MAX_OFFSET
        num_of_keys = div if rem == 0 else div + 1
        return ['%s:%s' % (key_prefix, k) for k in range(num_of_keys)]

    def calculate_key_and_offset(self, offset):
        return self.keys[offset // self.MAX_OFFSET], offset % self.MAX_OFFSET

    def __contains__(self, value):
        pipeline = self.connection.pipeline()

        hashed_offsets = self.calculate_offsets(value)
        for hashed_offset in hashed_offsets:
            key, offset = self.calculate_key_and_offset(hashed_offset)
            pipeline.getbit(key, offset)

        results = pipeline.execute()
        return all(results)

    def add(self, value, set_value=1, timeout=None):
        pipeline = self.connection.pipeline(transaction=True)

        hashed_offsets = self.calculate_offsets(value)
        for hashed_offset in hashed_offsets:
            key, offset = self.calculate_key_and_offset(hashed_offset)
            pipeline.setbit(key, offset, set_value)

            if timeout is not None:
                pipeline.expire(key, timeout)

        pipeline.execute()

    def delete(self, value):
        self.add(value, set_value=0)

    def calculate_offsets(self, key):
        # we're using only two hash functions with different settings, as described
        # by Kirsch & Mitzenmacher: http://www.eecs.harvard.edu/~kirsch/pubs/bbbf/esa06.pdf
        hash_1 = fnv_hash(key)
        hash_2 = ap_hash(key)

        for i in range(self.k):
            yield (hash_1 + i * hash_2) % self.n
