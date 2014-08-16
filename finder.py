import config

class Finder:
    def __init__(self):
        self.hosts = {}
        # make a reverse map
        for user in config.values['users']:
            for host in config.values['users'][user]['hosts']:
                self.hosts[host] = user

    def find_user(self, ip):
        return self.hosts[ip] if ip in self.hosts else None

    def user_hosts(self, user):
        return config.values['users'][user]['hosts']

    def check_type(self, user):
        return "any" if (user not in config.values['users'] or "check" not in config.values['users'][user]) else config.values['users'][user]['check']

    def save(self):
        with open(self.filename, 'w') as datafile:
            json.dump(datafile)
