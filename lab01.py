#!/usr/bin/env python3

from cmath import sqrt
from PIL import Image as Image
import math

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y, behavior = None):
    '''
    Returns the color value of a pixel given the (x, y) coordinates of the pixel, 
    the image, and the edge behavior. Accounts for No Behavior, Zero Behavior,
    Extend Behavior, and Wrap Behavior.

    For Zero Behavior, if the pixel is out-of-bounds, get_pixel returns 0 for the value of the pixel

    For Extend Behavior, if the pixel is out-of-bounds, get_pixel returns the value of the closest 
    edge-most pixel in-bounds.

    For Wrap Behavior, if the pixel is out-of-bounds, get_pixel returns the value of the pixel that
    wraps around to the other side of the picture that is in proportion to the position of the pixel.
    '''
    height = image['height']
    width = image['width']
    pixels = image['pixels']
    index = x + y*image['width']
    new_x = 0
    new_y = 0
    #when pixel is in-bounds
    if x >=0 and x < width and y >=0 and y < height: 
        return image['pixels'][index]
    #returns 0 if any item is out of bounds for behavior zero
    elif behavior == 'zero':
            return 0
    #x is less than range
    elif x < 0:
        if behavior == 'extend':
            new_x = 0
            if y < 0:
                new_y = 0
            elif y >= height:
                new_y = height-1
            else:
                new_y = y
        elif behavior == 'wrap':
            if x%width == 0:
                new_x = 0
            else:
                new_x = width - abs(x)%width
            if y < 0:
                if y%height == 0:
                    new_y = 0
                else:
                    new_y = height - abs(y)%height
            elif y >= height:
                new_y = abs(y)%height
            else:
                new_y = y
    #x is greater than range
    elif x >= width:
        if behavior == 'extend':
            new_x = width -1
            if y < 0:
                new_y = 0
            elif y >= height:
                new_y = height-1
            else:
                new_y = y
        elif behavior == 'wrap':
            new_x = abs(x) % width
            if y < 0:
                if y%height == 0:
                    new_y = 0
                else:
                    new_y = height - abs(y)%height
            elif y >= height:
                new_y = abs(y)%height
            else:
                new_y = y
    #x is in range
    else:
        new_x = x
        if behavior == 'extend':
            if y < 0:
                new_y = 0
            elif y >= height:
                new_y = height-1
        elif behavior == 'wrap':
            if y < 0:
                if y%height == 0:
                    new_y = 0
                else:
                    new_y = height - abs(y)%height
            elif y >= height:
                new_y = abs(y)%height
    return image['pixels'][new_x + new_y*image['width']]

def set_pixel(image, x, y, c):
    index = x + y*image['width']
    image['pixels'][index] = c


def apply_per_pixel(image, func):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:],
    }
    for x in range(image['width']):
        for y in range(image['height']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)

# HELPER FUNCTIONS

def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings 'zero', 'extend', or 'wrap',
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of 'zero', 'extend', or 'wrap', return
    None.

    Otherwise, the output of this function should have the same form as a 6.009
    image (a dictionary with 'height', 'width', and 'pixels' keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    {
        height: int,
        width: int,
        pixels: ['pixels']
    }
    """
    if boundary_behavior not in ['zero', 'extend', 'wrap']:
        return None
    #creates new directionary
    correlated_image = {
            'height': image['height'],
            'width': image['width'],
            'pixels': [0] * len(image['pixels']),
        } 
    #applies kernel to the image
    for i in range(len(image['pixels'])):    
        x_cord = i%image['width']
        y_cord = i// image['width']
        counter = 0
        applied_sum = 0
        for y in range(-(kernel['height']//2),1+ kernel['height']//2): 
            new_y = y_cord + y               
            for x in range(-(kernel['width']//2),1+ kernel['width']//2):
                new_x = x_cord + x
                applied_sum += get_pixel(image, new_x , new_y , boundary_behavior) * kernel['pixels'][counter]
                #counter to see which kernel index is being applied      
                counter+=1
        correlated_image['pixels'][i] = applied_sum
    return correlated_image

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    rounded_image = {
         'height': image['height'],
        'width': image['width'],
        'pixels': []
    }
    for i in range(len(image['pixels'])):
        if image['pixels'][i] > 255:
            rounded_image['pixels'].append(255)
        elif image['pixels'][i] < 0:
            rounded_image['pixels'].append(0)
        else:
            rounded_image['pixels'].append(round(image['pixels'][i]))
    return rounded_image

# FILTERS

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel = {
        'height' : n,
        'width' : n,
        'pixels' : [1/n**2 for i in range(n**2)]
         }

    # then compute the correlation of the input image with that kernel using
    # the 'extend' behavior for out-of-bounds pixels
    blurred_image = round_and_clip_image(correlate(image, kernel, 'extend'))

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    return blurred_image

def sharpened(image, n):
    """
    Returns a new image representing the resuting of applying an unsharp mask
    (with kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output. 
    """
    blurred_image = blurred(image, n)
    sharpened_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [2*image['pixels'][i] - blurred_image['pixels'][i] for i in range(len(image['pixels']))]
    }
    sharpened_image = round_and_clip_image(sharpened_image)
    return sharpened_image

def edges(image):
    """
    Returns a new image resulting from correlating the input with Kx and Ky
    then taking the square root of the sum of squares of corresponding pixels
    in Ox and Oy for each pixel in the new image. 

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output. 
    """
    Kx = {
        'height' : 3,
        'width' : 3,
        'pixels' : [-1, 0, 1, -2, 0, 2, -1, 0, 1]
         }
    Ky = {
        'height' : 3,
        'width' : 3,
        'pixels' : [-1, -2, -1, 0, 0, 0, 1, 2, 1]
         }
    Ox = correlate(image, Kx, 'extend')
    Oy = correlate(image, Ky, 'extend')
    Oxy_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [(((Ox['pixels'][i])**2 + (Oy['pixels'][i])**2))**(1/2) for i in range(len(image['pixels']))]
    }
    Oxy_image = round_and_clip_image(Oxy_image)
    return Oxy_image

# COLOR FILTERS

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def color_function(image):
        list_R = filt({
            'height': image['height'],
            'width': image['width'],
            'pixels': [image['pixels'][i][0] for i in range(len(image['pixels']))]
        })
        list_G = filt({
            'height': image['height'],
            'width': image['width'],
            'pixels': [image['pixels'][i][1] for i in range(len(image['pixels']))]
        })
        list_B = filt({
            'height': image['height'],
            'width': image['width'],
            'pixels': [image['pixels'][i][2] for i in range(len(image['pixels']))]
        })
        new_image = {
            'height': image['height'],
            'width' : image['width'],
            'pixels': [(list_R['pixels'][i], list_G['pixels'][i], list_B['pixels'][i]) for i in range(len(image['pixels']))]
        }
        return new_image
    return color_function

def make_blur_filter(n):
    def new_blur(image):
        return blurred(image, n)
    return new_blur

def make_sharpen_filter(n):
    def new_sharpen(image):
        return sharpened(image, n)
    return new_sharpen

def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def cascade_filters(image):
        new_image = image
        for filt in filters:
            new_image = filt(new_image)
        return new_image
    return cascade_filters

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()

'''Draws a black circle with given radius and center on an image'''
def circle(image, x, y, radius):
    new_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:]
    }
    for i in range(len(new_image['pixels'])):
        x_cord = i%image['width']
        y_cord = i// image['width']
        print (x_cord)
        distance_squared = ((x -x_cord)**2+ (y - y_cord)**2)
        if distance_squared == 0:
            distance_squared += 1
        distance = math.sqrt(distance_squared)
        if distance >= (radius - 10) and distance <= (radius + 10):
            set_pixel(new_image, x_cord, y_cord, 0)
    return new_image


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    bluegill = load_greyscale_image("C:\\6.009\\lab01\\test_images\\bluegill.png")
    print(len(bluegill['pixels']))
    save_color_image((circle(bluegill, 100, 100, 50)),"C:\\6.009\\lab01\\test_images\\circle_bluegill.png")
    # centered_pixel = load_greyscale_image("C:\\6.009\\lab01\\test_images\\centered_pixel.png")
    # print(blurred(centered_pixel, 7))
    # print(blurred(centered_pixel, 9))
    # rounded_image = {
    #      'height': 1,
    #     'width': 4,
    #     'pixels': [0, 255.2, 233.5, 260.1, -1]
    # }
    # kernel = {
    #     'height': 13,
    #     'width': 13,
    #     'pixels': [0] * 13**2 
    # }
    # kernel['pixels'][26] = 1
    # pigbird = load_greyscale_image("C:\\6.009\\lab01\\test_images\\pigbird.png")
    # save_greyscale_image(correlate(pigbird, kernel, 'zero'), "C:\\6.009\\lab01\\test_images\\correlate_extend_pigbird.png")
    # save_greyscale_image(correlate(pigbird, kernel, 'wrap'), "C:\\6.009\\lab01\\test_images\\correlate_wrap_pigbird.png")
    # cat = load_greyscale_image("C:\\6.009\\lab01\\test_images\\cat.png")
    # save_greyscale_image(blurred(cat, 13), "C:\\6.009\\lab01\\test_images\\blurred_cat.png")
    # python = load_greyscale_image("C:\\6.009\\lab01\\test_images\\python.png")
    # save_greyscale_image(sharpened(python, 11), "C:\\6.009\\lab01\\test_images\\sharpened_python.png")
    # construct = load_greyscale_image("C:\\6.009\\lab01\\test_images\\construct.png")
    # save_greyscale_image(edges(construct), "C:\\6.009\\lab01\\test_images\\edges_construct.png")
    # color_inverted = color_filter_from_greyscale_filter(inverted)
    # inverted_color_cat = color_inverted(load_color_image("C:\\6.009\\lab01\\test_images\\cat.png"))
    # save_color_image(inverted_color_cat,"C:\\6.009\\lab01\\test_images\\inverted_color_cat.png")
    # blurredd = make_blur_filter(9)
    # color_blurred = color_filter_from_greyscale_filter(blurredd)
    # blurred_color_python = color_blurred(load_color_image("C:\\6.009\\lab01\\test_images\\python.png"))
    # save_color_image(blurred_color_python,"C:\\6.009\\lab01\\test_images\\blurred_color_python.png")
    # sharp = make_sharpen_filter(7)
    # color_sharpened = color_filter_from_greyscale_filter(sharp)
    # sharp_color_sparrow = color_sharpened(load_color_image("C:\\6.009\\lab01\\test_images\\sparrowchick.png"))
    # save_color_image(sharp_color_sparrow,"C:\\6.009\\lab01\\test_images\\sharp_color_sparrowchick.png")
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    # filtered_frog =  filt(load_color_image("C:\\6.009\\lab01\\test_images\\frog.png"))
    # save_color_image(filtered_frog,"C:\\6.009\\lab01\\test_images\\filt_frog.png")
    # kernel = {
    #     'height': 3,
    #     'width': 3,
    #     'pixels': [0, 0, 0, 1, 0, 0, 0, 0, 0]
    # }
    # image = {
    #     'height': 2,
    #     'width': 2,
    #     'pixels': [1, 2, 3, 4] 
    # }
    # print(correlate(image, kernel, 'zero'))
    # kernel = {
    #     'height': 3,
    #     'width': 3,
    #     'pixels': [ 0.00,  -0.07,   0.00,
    #                 -0.45,   1.20,  -0.25,
    #                   0.00,  -0.12,   0.00]
    # }
    # test_image = {
    #     'height': 3,
    #     'width': 3,
    #     'pixels': [80,  53,   99,
    #                 129,   127,  148,
    #                   175,  174,   193]
    # }
    # circle(test_image, 1, 1, 1)

    # print(edges(test_image))
    # centered_pixel = load_greyscale_image("C:\\6.009\\lab01\\test_images\\centered_pixel.png")
    # print(edges(centered_pixel))
    # applied_correlate = correlate(test_image, kernel, 'wrap')
    # print(applied_correlate)
    #save_greyscale_image(correlate(pigbird, kernel, 'zero'),"C:\\6.009\\lab01\\test_images\\pigbirdy.png")
    # inverted_color = color_filter_from_greyscale_filter(inverted)
    # inverted_cat = inverted_color(load_color_image("C:\\6.009\\lab01\\test_images\\cat.png"))
    # save_color_image(inverted_cat, "C:\\6.009\\lab01\\test_images\\inverted_cat_color.png")
