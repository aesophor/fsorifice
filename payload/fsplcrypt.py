from interface.console import ui_console
import os
import sys
import py_compile


class fso_crypter(object):

    def __init__(self):
        # create some instances.
        self._ui_console = ui_console()


    def process_code(self, new_filename):
        self.bytecode = new_filename + 'c'
        self.opt = self.bytecode[:-4] + '-fsoc.py'

        try:
            py_compile.compile(new_filename, cfile = self.bytecode, dfile = None, doraise = False, )
            os.rename(self.bytecode, self.opt)
        except:
            self._ui_console.log("[!] Error: The specified payload is already crypted.")
            return -1

        return self.opt


    def checkpath(self):
        self._ui_console.note("[*] Crypting payload into bytecode...")

        while True:
            self.filename = raw_input("[+] Please enter the filename (please include extension): ")
            if os.path.isfile(self.filename):
                self.result = self.process_code(self.filename)
                if self.result != -1:
                    self.savepath = os.path.abspath(self.result)
                    print "[*] The payload has been crypted and saved to: " + self.savepath
                    break
                else:
                    print "[-] Unable to crypt the specified payload.\n"
            else:
                self._ui_console.log("[!] Error: the specified file not found.")
                continue
        print


    def Start(self):
        self.checkpath()
