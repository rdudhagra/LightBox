import time
import argparse
from threading import Thread
import random
from rpi_ws281x import PixelStrip

import scripts.color as colorUtil

class Led(Thread):

    # LED strip configuration:
    LED_COUNT = 95        # Number of LED pixels.
    LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
    # LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA = 10          # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 170  # Set to 0 for darkest and 255 for brightest
    LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
    FRAMERATE = 50

    def __init__(self):
        # Create NeoPixel object with appropriate configuration.
        self.strip = PixelStrip(self.LED_COUNT, \
                                self.LED_PIN, \
                                self.LED_FREQ_HZ, \
                                self.LED_DMA, \
                                self.LED_INVERT, \
                                self.LED_BRIGHTNESS//2, \
                                self.LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()

        # Variables that store what the LEDs will do

        self.loop = False   # whether the current sequence of frames should be
                            # repeated after completion
                    
        self.colorSeqs = {} # a dictionary storing color sequences 
                            # KEY: the key is arbitrary, to distinguish different color sequences
                            #      - It is up to the implementation to determine the key
                            # VAL: a list of colors, stored as integers, that form the sequence
                            #      - All values in colorSeqs must have the same length  

        self.seqLen = 0     # the length of color sequences in colorSeqs

        self.mapping = []   # a list containing integers
                            # these integers correspond to indices in colorSeqs
                            # length of mapping = number of LEDs in the LightBox

        self.currInd = 0    # an integer marking where in the color sequences the LEDs are

        self.targetBrightness = self.strip.getBrightness() # value storing brightness to be attained
                                                           # during gradual fade towards it


        # Initialize these variables for the first time (LEDs off)
        self.loop = False
        self.colorSeqs[0] = [0x000000]
        self.seqLen = 1
        self.mapping = [0] * self.strip.numPixels()
        self.currInd = 0
        # These settings will cause the LED's to switch to #000000 (off) once

        # Start thread that will handle LED changes in the background
        Thread.__init__(self)
        self.daemon = True

        print("Led Strip Initialized")

    # Continuous loop that handles LED changes registered in mapping and colorSeqs
    def run(self):
        while True:
            refreshStrip = True
            time.sleep(1.0 / self.FRAMERATE)

            if self.currInd == self.seqLen: #reached end of sequence
                if self.loop:
                    self.currInd = 0 #loop to beginning of sequence
                else:
                    refreshStrip = False

            if refreshStrip:
                try: 
                    for i in range(self.strip.numPixels()):
                        self.strip.setPixelColor(i, self.colorSeqs[self.mapping[i]][self.currInd])
                except KeyError:
                    print("Error: invalid key %d" % self.mapping[i])
                    continue
                self.currInd+=1

            if self.strip.getBrightness() != self.targetBrightness:
                self.strip.setBrightness( max( min( 
                        self.strip.getBrightness() + (self.FRAMERATE//25) * \
                        (1 if self.targetBrightness > self.strip.getBrightness() else -1) \
                    , 255), 0) \
                )
                if(abs(self.targetBrightness-self.strip.getBrightness())) < (self.FRAMERATE//25):
                    self.strip.setBrightness(self.targetBrightness)
                refreshStrip = True

            if refreshStrip:
                self.strip.show()


    # Color Manipulation functions...
    
    def solidColor(self, color):
        ''' Changes LightBox to a solid color, defined by color '''

        colorSeqs = {}
        mapping = [0] * self.strip.numPixels()

        # Iterate through each led in the strip
        for currLed in range(self.strip.numPixels()): 
            # Add entry to mapping for the color sequence
            mapping[currLed] = self.strip.getPixelColor(currLed)

            # Add sequence to colorSeqs if it doesn't exist already
            if mapping[currLed] not in colorSeqs:
                colorSeqs[mapping[currLed]] = \
                    colorUtil.linear_gradient(mapping[currLed], \
                                              color, \
                                              self.FRAMERATE//4)

        self.loop = False
        self.seqLen = self.FRAMERATE//4 
        self.currInd = 0
        self.mapping = mapping
        self.colorSeqs = colorSeqs

    def clear(self):
        '''clears all leds'''
        self.solidColor(0)

    def changeBrightness(self, newBrightnessValue):
        '''sets brightness of LEDs (0-100)'''
        self.targetBrightness = int(self.LED_BRIGHTNESS*newBrightnessValue**1.5/1000) #1000=100^1.5

    def rainbow(self):
        '''creates a rainbow sequence that loops'''

        #generates list of colors that cycle in hue
        numFrames = self.FRAMERATE * 10 # the number is how many seconds per rainbow cycle
        rainbowColors = [colorUtil.HSV_to_hex(k/numFrames*360, 1, 1) for k in range(0,numFrames,1)]

        colorSeqs = {}
        seqLen = len(rainbowColors)
        mapping = [0] * self.strip.numPixels()

        for led in range(self.strip.numPixels()):
            mapping[led] = led #unique mapping for each led
            colorSeqs[led] = [0]*seqLen
        
        for colorPos in range(seqLen):
            for led in range(self.strip.numPixels()):
                colorSeqs[led][colorPos] = rainbowColors[(colorPos+led) % seqLen]

        self.loop = True
        self.seqLen = seqLen
        self.currInd = 0
        self.colorSeqs = colorSeqs
        self.mapping = mapping
            

    def sparkle(self, seqLenSeconds = 30):
        '''creates a sparkle sequence that loops'''

        numFrames = self.FRAMERATE * 1 # the number is how many seconds for average flash
        deviation = self.FRAMERATE // 2 # random deviation of the flash lengths
        satChoice = ([0.0]) + ([0.5]*5) + ([1]*50) # weighted probability for saturation
                                                   # prevents too many 'white' LEDs
        valChoice = ([0.2]) + ([0.5]*5) + ([1]*10) # weighted probability for value
                                                   # prevents too many dim LED's

        colorSeqs = {}
        seqLen = numFrames * seqLenSeconds
        mapping = [0] * self.strip.numPixels()

        for led in range(self.strip.numPixels()):
            mapping[led] = led # unique mapping for each led
            colorSeqs[led] = [0]*seqLen
        
        for colorPos in range(seqLen):

            for i in range(random.randrange(0,4)): # repeat a random number of times
                                                   # to create variety

                led = random.randrange(0, self.strip.numPixels())
                if colorSeqs[led][colorPos] != 0: # already a flash at that led
                    continue # don't overwrite it
                duration = random.randint(numFrames-deviation, numFrames+deviation)
                hue = random.uniform(0,360)
                sat = random.choice(satChoice)
                val = random.choice(valChoice)

                for k in range(duration):
                    # fill in colorSeqs for the flash, given by the piecewise function
                    # at https://www.desmos.com/calculator/lmsoc2uoif
                    colorSeqs[led][(colorPos+k)%seqLen] = colorUtil.HSV_to_hex(hue, sat, \
                        val * ( (3/duration)*k if k < duration/3 \
                        else (-3/(2*duration))*(k-duration) ) \
                    )

        self.loop = True
        self.seqLen = seqLen
        self.currInd = 0
        self.colorSeqs = colorSeqs
        self.mapping = mapping