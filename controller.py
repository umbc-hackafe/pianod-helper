import telnetlib
from threading import Lock

class Controller:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.user = username
        self.pw = password

        self.lock = Lock()

        self.first_login()

    def first_login(self):
        with self.lock:
            self.conn = telnetlib.Telnet(self.host, self.port)
            self.conn.write("USER {} {}".format(self.user, self.pw).encode('ascii') + b'\n')
            self.conn.write("AUTOTUNE MODE FLAG".encode('ascii') + b'\n')

    def check_users(self, users):
        users_found = set()

        with self.lock:
            # throw away old data jic
            self.conn.read_eager()
            self.conn.write("USERS LIST".encode('ascii') + b'\n')
            user_results = self.conn.read_until(b"204")
            for line in user_results.decode('ascii').splitlines():
                if line.startswith("111"):
                    user = line.split()[2]
                    users_found.add(user)
                    print("Found user {}".format(user))

            for user in set(users) - users_found:
                print("Creating user {}".format(user))
                self.conn.write("CREATE USER {} {}".format(user, user).encode('ascii') + b'\n')
                self.conn.write("GRANT influence TO {}".format(user).encode('ascii') + b'\n')
        self.users_created = True

    def rate(self, mode, user, pw):
        with self.lock:
            self.conn.write("AS USER {} {} RATE {}".format(user, pw, mode).encode('ascii') + b'\n')

    def online_users(self, users):
        with self.lock:
            self.conn.write("AUTOTUNE FOR {}".format(" ".join(users)).encode('ascii') + b'\n')

    def login(self, user):
        with self.lock:
            self.conn.write("AUTOTUNE CONSIDER {}".format(user).encode('ascii') + b'\n')

    def logout(self, user):
        with self.lock:
            self.conn.write("AUTOTUNE DISREGARD {}".format(user).encode('ascii') + b'\n')

    def close(self):
        with self.lock:
            self.conn.write("QUIT".encode('ascii') + b'\n')
            self.conn.close()
