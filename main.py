#!/usr/bin/env python
from flask import Flask, request, abort, g
from werkzeug.local import LocalProxy
import finder
import controller
import pinger
import signal
import sys
from time import sleep

app = Flask(__name__)

def get_pianod():
    with app.app_context():
        pianod = getattr(g, '_pianod', None)
        if pianod is None:
            pianod = controller.Controller()
        return pianod

def get_finder():
    with app.app_context():
        thefinder = getattr(g, '_finder', None)
        if thefinder is None:
            thefinder = finder.Finder()
        return thefinder

pianod = LocalProxy(get_pianod)
thefinder = LocalProxy(get_finder)

def get_pinger():
    with app.app_context():
        thepinger = getattr(g, '_pinger', None)
        if thepinger is None:
            thepinger = pinger.Pinger(thefinder, pianod)
        return thepinger

thepinger = LocalProxy(get_pinger)

def signal_handler(signal, frame):
    print("Caught signal. Exiting...")
    pianod.close()
    thepinger.stop()
    sys.exit(0)

@app.route('/')
def main():
    return "API URLs:\n/rate/good\n/rate/bad\n/control/pause\n/control/play\n/control/playpause\n/control/stop\n/control/start\n/station/auto\n/station/<name>"

@app.route('/rate/<rating>')
def rate(rating):
    if not rating or rating.upper() not in ("GOOD", "BAD"):
        return "Invalid rating: {}".format(rating)
        abort(400)

    ip = request.remote_addr
    user = thefinder.find_user(ip)

    if user:
        pianod.rate(rating.upper(), user, user)
        return "OK"
    else:
        return "No user registered at your IP"
        abort(403)

@app.route('/skip')
def skip():
    pianod.skip()
    return "OK"

@app.route('/pause')
def pause():
    pianod.pause()
    return "OK"

@app.route('/play')
def play():
    pianod.play()
    return "OK"

@app.route('/stop/<now>')
@app.route('/stop')
def stop(now=True):
    pianod.stop(now)
    return "OK"

@app.route('/playpause')
def playpause():
    pianod.pause(toggle=True)
    return "OK"

@app.teardown_appcontext
def teardown_finder(exception):
    thefinder = getattr(g, '_finder', None)
    if thefinder is not None:
        thefinder.save()

@app.teardown_appcontext
def teardown_pianod(exception):
    pianod = getattr(g, '_pianod', None)
    if pianod is not None:
        pianod.close()

@app.teardown_appcontext
def teardown_pinger(exception):
    thepinger = getattr(g, '_pinger', None)
    if thepinger is not None:
        thepinger.save()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    get_pianod().check_users()
    get_pinger().start()
    app.run(host='0.0.0.0')
