# No Imports Allowed!

'''Reverses samples in the sound dictionary'''
def backwards(sound):
    reverse = sound['samples'][::-1]
    new_dict = {
        'rate': sound['rate'],
        'samples': reverse,
    }
    return new_dict

'''combines two sound dictionaries that are each manipulated by p'''
def mix(sound1, sound2, p):
    if (sound1['rate'] != sound2['rate']):
        return None
    else:
        mix_sound = {'rate': sound1['rate'], 'samples': []}
        # for i in range(len(sound1['samples'])):
        #     sound1['samples'][i] *= p
        # for i in range(len(sound2['samples'])):
        #     sound2['samples'][i] *= 1-p
        smallest = min(len(sound1['samples']), len(sound2['samples'])) 
        #adds altered samples from each sound together and appends them to new mix_sound
        for i in range(smallest):
            mix_sound['samples'].append(sound1['samples'][i]*p+sound2['samples'][i]*(1-p))
        # mix_sound['samples'] = [sound1['samples'][i]*p+sound2['samples'][i]*(1-p) for i in range(smallest)]
        return mix_sound


        

'''Applies a kernel effect to a sound dictionary's samples'''
def convolve(sound, kernel):
    original = sound["samples"] + ([0] * (len(kernel) - 1))
    current = [0] * (len(sound['samples']) + len(kernel) - 1)
    convolve_sound = {
            'rate': sound['rate']
        }
    #uses shift helper function to shift and modify elements in a samples list
    for i in range(len(kernel)):
        shifted = shift(original, i, kernel[i])
        for i in range(len(original)):
            current[i] = current[i] + shifted[i]
    convolve_sound['samples'] = current
    return convolve_sound

#helper function to shift lists by kernel index and multiply elements by value in kernel
def shift(list, index, factor):
    a_list = [0]*len(list)
    for i in range(len(list)):
        a_list[(i+index) % len(list)] = list[i] * factor
    return a_list
        
'''Creates an echo of the original recording based on how many echoes are present,
how much delay is inbetween echoes, and the scale-down effect so echoes get
quieter as they progress '''
def echo(sound, num_echoes, delay, scale):
    sample_delay = round(delay * sound['rate'])
    original = sound['samples'] + [0] * num_echoes * sample_delay
    current = sound['samples'] + [0] * num_echoes * sample_delay
    echo_sound = {
            'rate': sound['rate']
        }
    #adds echoed samples to the current sound sample list
    for i in range(1, num_echoes + 1):
        echo = shift(original, i * sample_delay, scale**i)
        for j in range(len(current)):
            current[j] += echo[j]
    echo_sound['samples'] = current
    return echo_sound

'''apply pan affect and scale to samples'''
def pan(sound): 
    s = {
    'rate': sound['rate'],
    'left': [],
    'right': []
    }
    for i in range(len(sound['left'])):
        s['right'].append(sound['right'][i]*i/(len(sound['left'])-1))
        s['left'].append(sound['left'][i]*(1-i/(len(sound['left'])-1)))
    return(s)

'''Subtracts left from right sample to switch from stereo to mono 
    in order to remove vocals'''
def remove_vocals(sound):
    s = {
        'rate': sound['rate'],
        'samples': []
    }
    for i in range(len(sound['left'])):
        s['samples'].append(sound['left'][i] - sound['right'][i])
    return s


def bass_boost_kernel(N, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    kernel = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    for i in range(N):
        kernel = convolve(kernel, base['samples'])
    kernel = kernel['samples']

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel)//2] += 1

    return kernel


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {'rate': sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left.append(struct.unpack('<h', frame[:2])[0])
                right.append(struct.unpack('<h', frame[2:])[0])
            else:
                datum = struct.unpack('<h', frame)[0]
                left.append(datum)
                right.append(datum)

        out['left'] = [i/(2**15) for i in left]
        out['right'] = [i/(2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left = struct.unpack('<h', frame[:2])[0]
                right = struct.unpack('<h', frame[2:])[0]
                samples.append((left + right)/2)
            else:
                datum = struct.unpack('<h', frame)[0]
                samples.append(datum)

        out['samples'] = [i/(2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')

    if 'samples' in sound:
        # mono file
        outfile.setparams((1, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = [int(max(-1, min(1, v)) * (2**15-1)) for v in sound['samples']]
    else:
        # stereo
        outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = []
        for l, r in zip(sound['left'], sound['right']):
            l = int(max(-1, min(1, l)) * (2**15-1))
            r = int(max(-1, min(1, r)) * (2**15-1))
            out.append(l)
            out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    hello = load_wav('sounds/hello.wav')
    #mystery = load_wav('sounds/mystery.wav')
    #write_wav(backwards(mystery), 'backwards_mystery.wav')
    #synth = load_wav('sounds/synth.wav')
    #water = load_wav('sounds/water.wav')
    #write_wav(mix(synth, water, 0.2), 'mix_sounds.wav')
    # write_wav(backwards(hello), 'hello_reversed.wav')
    # s = {
    # 'rate': 30,
    # 'samples': [-5, 0, 2, 3, 4],
    # }
    # k = [0, 1, 0, 0, 3]
    # print(convolve(s, k))
    # ice_and_chilli = load_wav('sounds/ice_and_chilli.wav')
    # kernel = bass_boost_kernel(1000, scale = 1.5)
    # write_wav(convolve(ice_and_chilli, kernel), 'convolve_sound.wav')
    # chord = load_wav('sounds/chord.wav')
    # write_wav(echo(chord, 5, 0.3, 0.6), 'echo_chord.wav')
    # car = load_wav('sounds/car.wav', stereo=True)
    # write_wav(pan(car), 'pan_car.wav')
    lookout_mountain = load_wav('sounds/lookout_mountain.wav', stereo=True)
    write_wav(remove_vocals(lookout_mountain), 'remove_vocals.wav')