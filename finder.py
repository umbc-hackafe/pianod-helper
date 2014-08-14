import json

class InvalidConfigurationException(Exception):
    pass

class Finder:
    def __init__(self, filename):
        self.filename = filename
        with open(filename, 'r') as datafile:
            data = json.load(datafile)
        if data and "users" in data:
            self.users = data["users"]
            self.hosts = {}
            # make a reverse map
            for user in self.users:
                for host in self.users[user]["hosts"]:
                    self.hosts[host] = user
        else:
            raise InvalidConfigurationException()

    def find_user(self, ip):
        return self.hosts[ip] if ip in self.hosts else None

    def user_hosts(self, user):
        return self.users[user]["hosts"]

    def check_type(self, user):
        return "any" if (user not in self.users or "check" not in self.users[user]) else self.users[user]["check"]

    def save(self):
        with open(self.filename, 'w') as datafile:
            json.dump(datafile)
