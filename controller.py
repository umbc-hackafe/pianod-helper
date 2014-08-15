import telnetlib
class Controller:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.conn = telnetlib.Telnet(host, port)
        self.conn.write("USER {} {}".format(username, password).encode('ascii') + b'\n')
        self.conn.write("AUTOTUNE MODE FLAG".encode('ascii') + b'\n')

    def check_users(self, users):
        users_found = set()
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

    def rate(self, mode, user, pw):
        self.conn.write("AS USER {} {} RATE {}".format(user, pw, mode).encode('ascii') + b'\n')

    def online_users(self, users):
        self.conn.write("AUTOTUNE FOR {}".format(" ".join(users)).encode('ascii') + b'\n')

    def login(self, user):
        self.conn.write("AUTOTUNE CONSIDER {}".format(user).encode('ascii') + b'\n')

    def logout(self, user):
        self.conn.write("AUTOTUNE DISREGARD {}".format(user).encode('ascii') + b'\n')

    def close(self):
        self.conn.close()
