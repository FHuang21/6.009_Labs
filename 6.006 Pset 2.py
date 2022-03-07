import math
 
def search_lyrics(L, Q):
    """
    Input: L | an ASCII string 
    Input: Q | an ASCII string where |Q| < |L|
    
    Return `True` if Q appears inside the lyrics L and `False` otherwise.
    """
    PRIME = 2 ** 31 - 1
    query_hash = 0
    current_hash = 0
    
    index = 0 
    for i in Q:
        query_hash = (query_hash + (ord(i) * 128**(len(Q) -1 - index))%PRIME)%PRIME
        index += 1
    
    for index, ele in enumerate(L):
        if index == 0:
            for i in range(len(Q)):
                current_hash = (current_hash + (ord(L[i]) * 128**(len(Q) -1 - i))%PRIME)%PRIME
        if query_hash == current_hash:
            return True
        else:
            # current_hash = (current_hash - (ord(ele)∗128∗∗(len(Q)−1))%PRIME)%PRIME
            # current_hash = (current_hash ∗128%PRIME)%PRIME

            current_hash = ( ( ((current_hash - (ord(ele)*128**(len(Q)-1)))%PRIME)%PRIME ) * 128%PRIME ) % PRIME
            if index + len(Q) < len(L):
                current_hash = (current_hash + (ord(L[index + len(Q)]))%PRIME)%PRIME
            else:
                pass
    return False



if __name__ == "__main__":

    # PRIME = 2 ** 31 - 1
    # query_hash = 0
    # counter = 0 
    # for i in "what ":
    #     query_hash = (query_hash + (ord(i) * 128**(len("what ") -1 - counter))%PRIME)%PRIME
    #     counter += 1
    


    # print(query_hash)
   pass