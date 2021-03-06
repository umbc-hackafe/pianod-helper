import finder
import controller
import config
from threading import Thread
from time import sleep
from os import devnull
from subprocess import check_call, CalledProcessError, STDOUT

class Pinger:
    def __init__(self, thefinder, thecontroller):
        self.finder = thefinder
        self.controller = thecontroller
        self.statuses = {}
        self.keepgoing = True
        self.stopped = False

        for user in config.values['users']:
            self.statuses[user] = None

    def ping_host(self, host):
        with open(devnull, 'wb') as null:
            try:
                check_call(['ping', '-c', '1', host], stdout=null, stderr=STDOUT)
                result = True
            except CalledProcessError:
                result = False
            except:
                result = False
        return result

    def ping_user(self, user):
        if user and user in self.statuses:
            hosts_up = 0

            check_type = self.finder.check_type(user)

            for host in self.finder.user_hosts(user):
                result = self.ping_host(host)
                if result:
                    hosts_up += 1
                    if check_type == "any":
                        break

            if check_type == "all":
                result = hosts_up == len(self.finder.user_hosts(user))
            elif type(check_type) is int or check_type.isdigit():
                result = hosts_up > int(check_type)
            else: # check_type == "any" goes here
                result = hosts_up > 0

            if result != self.statuses[user]:
                if result:
                    self.controller.login(user)
                else:
                    self.controller.logout(user)
                self.statuses[user] = result

                if True not in self.statuses.values():
                    self.controller.stop()

    def start(self):
        self.thread = Thread(target=self.run, name="pinger", daemon=True)
        self.thread.start()

    def run(self):
        # start thread
        while self.keepgoing:
            for user in config.usernames():
                if not self.keepgoing:
                    break
                self.ping_user(user)

            sleep(config.values["ping"]["sleep"])
        self.stopped = True

    def stop(self):
        self.keepgoing = False
