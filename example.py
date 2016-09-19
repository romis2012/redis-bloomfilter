# -*- coding: utf-8 -*-
from bloomfilter import BloomFilter
from redis import Redis

urls = BloomFilter(connection=Redis.from_url('redis://localhost:6380'), key_prefix='bloom', num_bits=1024, num_hashes=8)
urls.add('https://www.google.ru/')
urls.add('http://yandex.ru/')
urls.add('https://www.python.org/')
urls.add('https://www.quora.com/')
urls.add('http://stackoverflow.com/')

assert 'https://www.quora.com/' in urls
assert 'https://www.microsoft.com/' not in urls





