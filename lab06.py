from math import remainder
from operator import ne
import sys

from pyparsing import empty
from http009 import http_response

import typing
import doctest

sys.setrecursionlimit(10000)

# NO ADDITIONAL IMPORTS!


# custom exception types for lab 6


class HTTPRuntimeError(Exception):
    pass


class HTTPFileNotFoundError(FileNotFoundError):
    pass


#helper functions
# def manifest(r, chunksize):
#     url_list = []
#     next_line = 's'
#     while next_line:
#         next_line = r.readline().strip()
#         if next_line != '--' and next_line != '':
#             url_list.append(next_line)
#         else:
#             for ele in url_list:
#                 try:
#                     yield from download_file(ele, chunksize)
#                     url_list = []
#                     break
#                 except:
#                     pass         
            



# functions for lab 6

def download_file(url, chunk_size=8192):
    """
    Yield the raw data from the given URL, in segments of at most chunk_size
    bytes (except when retrieving cached data as seen in section 2.2.1 of the
    writeup, in which cases longer segments can be yielded).

    If the request results in a redirect, yield bytes from the endpoint of the
    redirect.

    If the given URL represents a manifest, yield bytes from the parts
    represented therein, in the order they are specified.

    Raises an HTTPRuntimeError if the URL can't be reached, or in the case of a
    500 status code.  Raises an HTTPFileNotFoundError in the case of a 404
    status code.
    """


    #check if url is valid
    try:
        r = http_response(url)
    except:
        raise HTTPRuntimeError

    #Checking status codes

    #File not found error
    if r.status == 404:
        raise HTTPFileNotFoundError
    
    #Error on server Error
    elif r.status == 500:
        raise HTTPRuntimeError
    
    #Redirect status code
    elif r.status == 301 or r.status == 302 or r.status == 307:
        recurse_url = r.getheader('location')
        yield from download_file(recurse_url, chunk_size)

    #checks if url represents a file manifest
    elif url[-6:] == '.parts' or r.getheader('content-type') == 'text/parts-manifest':
        url_list = []
        next_line = 's'
        cache = {}
        cache_flag = False
        while next_line:
            next_line = r.readline().strip()
            if next_line != b'--' and next_line != b'':
                url_list.append(next_line)
            else:

                if b'(*)' in url_list:
                    cache_flag = True
                for ele in url_list:
                    if cache_flag and ele in cache:
                        yield cache[ele]
                        break
                    try:
                        data = b''
                        for i in download_file(ele, chunk_size):
                            data += i
                            yield i
                        if cache_flag:
                            cache[ele] = data
                            cache_flag = False
                        url_list = []
                        break
                    except:
                        pass 
        #yield from manifest(r, chunk_size)

    #Status code 200: successful request
    else:
        current_yield = r.read(chunk_size)
        while current_yield != b'':
            yield current_yield
            current_yield = r.read(chunk_size)

#helper function
def big_endian(bstring):
    '''
    Given a bytestring, returns the big_endian value
    '''
    num1 = 256**3 * bstring[0]
    num2 = 256**2 * bstring[1]
    num3 = 256 * bstring[2]
    num4 = bstring[3]
    return num1+num2+num3+num4

def files_from_sequence(stream):
    """
    Given a generator from download_file that represents a file sequence, yield
    the files from the sequence in the order they are specified.
    """
    bstring = bytearray()
    bool = True
    add_length = True
    for data in stream:
        #add if length of bstring < 4
        if add_length == True:
            bstring.extend(data)
            add_length = False
        #loop while add condition is False
        while add_length == False:
            #only done the first time when finding the length of given sequence
            if len(bstring) >= 4 and bool == True:
                size = big_endian(bstring)
                bstring = bstring[4:]
                bool = False
            #exit while is bstring length is less than 4
            elif len(bstring) < 4:
                add_length = True
            else: #bool is False
                if len(bstring) >= size: 
                    yield bytes(bstring[:size])
                    bstring = bstring[size:]
                    bool = True
                else:
                    add_length = True
    

if __name__ == "__main__":
    # url = 'http://py.mit.edu'
    # r = http_response(url)
    # print(r.getheader('location'))
    #url = 'http://mit.edu/6.009/www/lab6_examples/cornsnake.jpg.parts'
    # a = open(sys.argv[2], 'wb')
    # a.write(b''.join(download_file(sys.argv[1])))
    
    file = files_from_sequence(download_file(sys.argv[1]))
    for i in range(53):
        f = open(f'{sys.argv[2]}_file{i+1}', 'wb')    
        f.write(next(file))


