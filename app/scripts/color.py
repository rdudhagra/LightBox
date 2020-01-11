import math

def hexStr_to_hexInt(hexStr):
    ''' "#FFFFFF" -> 0xFFFFFF '''
    return int(hexStr.lstrip('#'), 16)

def hex_to_RGB(hexInt):
    ''' 0xFFFFFF -> [255,255,255] '''
    return ((hexInt >> 16) & 255, (hexInt >> 8) & 255, hexInt & 255)


def RGB_to_hex(RGB):
    ''' [255,255,255] -> 0xFFFFFF '''
    # Components need to be integers for hex to make sense
    return (RGB[0]<<16) + (RGB[1]<<8) + RGB[2]

def HSV_to_hex(h, s, v):
    ''' [0,1,1] -> [255,0,0] (Hue: 0-360, Sat/Val: 0-1)'''
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return RGB_to_hex((r,g,b))


def linear_gradient(start_hex, finish_hex=0xFFFFFF, n=10):
    ''' returns a gradient list of (n) colors between
      two hex colors. start_hex and finish_hex
      should be the full six-digit color hex '''
    # Starting and ending colors in RGB form
    s = hex_to_RGB(start_hex)
    f = hex_to_RGB(finish_hex)
    # Initilize a list of the output colors with the starting color
    RGB_list = [start_hex]
    # Calcuate a color at each evenly spaced value of t from 1 to n
    for t in range(1, n):
        # Interpolate RGB vector for color at the current value of t
        curr_vector = [
            int(s[j] + (float(t)/(n-1))*(f[j]-s[j]))
            for j in range(3)
        ]
        # Add it to our list of output colors
        RGB_list.append(RGB_to_hex(curr_vector))

    return RGB_list

def adj_brightness(hexcolor, brightness):
    '''takes in a hex int and multiplies the r,g,b
    values by the decimal value "brightness" (0-1)'''
    return RGB_to_hex([int(z * brightness) for z in hex_to_RGB(hexcolor)])