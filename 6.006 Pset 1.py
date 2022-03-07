##################################################
##  Problem 3.4. Find order
##################################################

# Given a list of positive integers and the starting integer d, return x such that x is the smallest value greater than
# or equal to d that's not present in the list
from xml.etree.ElementPath import find


def find_first_missing_element(arr, d):
    '''
    Inputs: 
        arr        (list(int)) | List of sorted, unique positive integer order id's
        d          (int)       | Positive integer of smallest possible value in arr
    Output: 
        -          (int)       | The smallest integer greater than or equal to d that's not present in arr
    '''
    ##################
    # YOUR CODE HERE #
    ################## 
    #middle index element
   #checks base case of if array is len 0
    if not arr:
        return d
    #checks base case of if array is len 1
    if len(arr) == 1:
        if arr[0] > d:
            return d
        else:
            return d+1
    #recurse through either first or second half of the list
    if arr[len(arr) // 2] == d + len(arr) // 2:
        #checks right half
        return find_first_missing_element(arr[len(arr) // 2:], arr[len(arr) // 2]) 
    else:
        #checks left half
        return find_first_missing_element(arr[:len(arr) // 2], d) 
