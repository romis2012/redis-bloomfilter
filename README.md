# redis-bloomfilter
Simple Redis-backed bloom filter.
Based on [bloomfilter-redis](https://github.com/xupeng/bloomfilter-redis) project, 
but has no limit to 2<sup>32</sup>-1 (512 MB) filter size (number of bits).


## Example

    from redis import Redis
    from bloomfilter import BloomFilter
    
    urls = BloomFilter(connection=Redis(), key_prefix='bloom', num_bits=1024, num_hashes=8)
    urls.add('https://www.google.ru/')
    urls.add('http://yandex.ru/')
    urls.add('https://www.python.org/')
    urls.add('https://www.quora.com/')
    urls.add('http://stackoverflow.com/')
    
    assert 'https://www.quora.com/' in urls
    assert 'https://www.microsoft.com/' not in urls