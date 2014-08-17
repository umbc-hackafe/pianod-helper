import config
import telnetlib
from threading import Lock

g_conn = None

class Controller:
    def __init__(self, host=config.values['pianod']['host'],
                 port=config.values['pianod']['port'],
                 username=config.values['pianod']['user'],
                 password=config.values['pianod']['pass']):
        self.host = host
        self.port = port
        self.user = username
        self.pw = password

        self.lock = Lock()

        self.stopped = True
        self.first_login()

    def first_login(self):
        with self.lock:
            global g_conn
            if g_conn:
                self.conn = g_conn
            else:
                self.conn = telnetlib.Telnet(self.host, self.port)
                g_conn = self.conn
            try:
                self.conn.write("USER {} {}".format(self.user, self.pw).encode('ascii') + b'\n')
                self.conn.write("AUTOTUNE MODE FLAG".encode('ascii') + b'\n')
                return True
            except BrokenPipeError:
                return False

    def cmd(self, command, lock=True):
        success = False
        while not success:
            try:
                if lock:
                    with self.lock:
                        self.conn.write(command.encode('ascii') + b'\n')
                else:
                    self.conn.write(command.encode('ascii') + b'\n')
                success = True
            except BrokenPipeError:
                self.close()
                while not self.first_login():
                    pass

    def check_users(self):
        success = False
        while not success:
            users = config.usernames()
            users_found = set()

            try:
                with self.lock:
                    # throw away old data jic
                    self.conn.read_eager()
                    self.cmd("USERS LIST", lock=False)
                    user_results = self.conn.read_until(b"204")
                    for line in user_results.decode('ascii').splitlines():
                        if line.startswith("111"):
                            user = line.split()[2]
                            users_found.add(user)
                success = True

            except BrokenPipeError:
                self.close()
                while not self.first_login():
                    pass

        for user in set(users) - users_found:
            self.cmd("CREATE USER {} {}".format(user, user))
            self.cmd("GRANT influence TO {}".format(user))

        self.users_created = True

    def rate(self, mode, user, pw):
        self.cmd("AS USER {} {} RATE {}".format(user, pw, mode))

    def online_users(self, users):
        self.cmd("AUTOTUNE FOR {}".format(" ".join(users)))

    def stop(self, now=False):
        self.cmd("STOP{}".format(" NOW" if now else ""))
        self.stopped = True

    def login(self, user):
        self.cmd("AUTOTUNE CONSIDER {}".format(user))
        if self.stopped:
            self.cmd("PLAY MIX")
            self.stopped = False

    def pause(self, toggle=False):
        self.cmd("PLAYPAUSE" if toggle else "PAUSE")

    def play(self):
        if self.stopped:
            self.cmd("PLAY MIX")
        self.cmd("PLAY")

    def skip(self):
        self.cmd("SKIP")


    def logout(self, user):
        self.cmd("AUTOTUNE DISREGARD {}".format(user))

    def close(self):
        with self.lock:
            try:
                self.conn.write("QUIT".encode('ascii') + b'\n')
                self.conn.close()
            except BrokenPipeError:
                pass
            self.conn = None
            global g_conn
            g_conn = None
