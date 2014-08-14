import telnetlib
class Controller:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.conn = telnetlib.Telnet(host, port)
        self.conn.write("USER admin admin".encode('ascii') + b'\n')
        self.conn.write("AUTOTUNE MODE FLAG".encode('ascii') + b'\n')

    def rate(self, mode, user):
        self.conn.write("AS USER {} RATE {}".format(user, mode).encode('ascii') + b'\n')

    def online_users(self, users):
        self.conn.write("AUTOTUNE FOR {}".format(" ".join(users)).encode('ascii') + b'\n')

    def login(self, user):
        self.conn.write("AUTOTUNE CONSIDER {}".format(user).encode('ascii') + b'\n')

    def logout(self, user):
        self.conn.write("AUTOTUNE DISREGARD {}".format(user).encode('ascii') + b'\n')

    def close(self):
        self.conn.close()
