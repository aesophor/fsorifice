from interface.console import ui_console
from os                import path
import string


class fso_generator(object):

    def __init__(self):
        # define some global variables.
        self.RHOST       = ""
        self.RPORT       = ""
        self.DROPNAME    = ""

        # location to save to.
        self.DEST        = ""

        # create some instances.
        self._ui_console = ui_console()


    def process_code(self, platform, new_filename):
        new_filename = new_filename + '.py'

        if platform == '1':
            self.DEST = 'payload/template/linux.py'
        elif platform == '2':
            self.DEST = 'payload/template/windows.py'
        elif platform == '3':
            self.DEST = 'payload/template/osx.py'
        elif platform == '4':
            self.DEST = 'payload/template/android.py'
        else:
            print "[-] The specified platform does not exist."


        self.f1 = open(self.DEST, 'r')
        self.f2 = open(new_filename, 'w')

        for self.line in self.f1:
            if self.line.find('RHOST_TEMPLATE') != -1:
                self.f2.write(self.line.replace('RHOST_TEMPLATE', self.RHOST))
            elif self.line.find('RPORT_TEMPLATE') != -1:
                self.f2.write(self.line.replace('RPORT_TEMPLATE', self.RPORT))
            elif self.line.find('DROPNAME_TEMPLATE') != -1:
                self.f2.write(self.line.replace('DROPNAME_TEMPLATE', self.DROPNAME))
            else:
                self.f2.write(self.line)

        self.f1.close()
        self.f2.close()

        return new_filename


    def checkpath(self):
        self._ui_console.note("[*] Generating payload...")

        while True:
            self.os_code  = raw_input("[+] Please select the platform (1=Linux, 2=Windows, 3=OSX, 4=Android): ")
            self.filename = raw_input("[+] Please enter the filename (without extension): ")
            if path.isfile(self.filename):
                self._ui_console.log("[!] Error: filename already exists.")
                continue
            else:
                print "[*] The payload has been saved to: " + path.abspath(self.process_code(self.os_code, self.filename))
                break
        print


    def Start(self, rhost_input, rport_input, dropname_input):
        self.RHOST    = rhost_input
        self.RPORT    = str(rport_input)
        self.DROPNAME = dropname_input
        self.checkpath()
