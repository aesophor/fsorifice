import os
import subprocess


class shellexec(object):

    def __init__(self):
        # defining original & current working dir.
        self.owd = os.getcwd()
        self.cwd = self.owd

    def restore_wd(self):
        self.cwd = self.owd
        os.chdir(self.cwd)

    def shell_handler(self, command):
        # execute the shell command.
        self.proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        # renew cwd (if the user changes it).
        if command.startswith('cd '):
            os.chdir(command.split('cd ')[1])
            self.cwd = os.getcwd()

        # read the output.
        self.stdout_value = self.proc.stdout.read() + self.proc.stderr.read()

        # return the output.
        return self.stdout_value

    def Run(self, command):
        return self.shell_handler(command)
