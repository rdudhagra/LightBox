# imports
from flask import Flask, render_template, request, jsonify
import scripts.ledctrl as ledCtrl
import scripts.color as colorUtil
import time

# initialize flask
app = Flask(__name__)

# initialize LED
led = ledCtrl.Led()

# routes

@app.before_first_request
def before_first_request():
    print('########### Restarted, first request made ###########')
    led.start()

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/solidcolor', methods=['POST'])
def changeToSolidColor():
    newColor = request.form.get('color')
    print("Setting solid color to %s" % newColor)
    led.solidColor(colorUtil.hexStr_to_hexInt(newColor))
    return ""

@app.route('/brightnesschange', methods=['POST'])
def changeBrightness():
    newBrightness = request.form.get('brightness')
    print("Setting brightness to %s%%" % newBrightness)
    led.changeBrightness(int(newBrightness))
    return ""

@app.route('/pattern', methods=['POST'])
def startPattern():
    pattern = request.form.get('pattern')
    if pattern == "rainbow":
        print("Starting rainbow...")
        led.rainbow()
    elif pattern == "sparkle":
        print("Starting sparkle...")
        led.sparkle()
    else:
        print("Invalid pattern: %s" % pattern)
    return ""

import atexit
atexit.register(led.clear)

# run the server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='80')