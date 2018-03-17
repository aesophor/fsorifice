import win32gui
import win32ui
import win32con
import win32api
import Image


class fso_screenlogger(object):

    def __init__(self):
        # screenshot quality. 0=lowest, 1=medium, 2=high.
        self.quality = [(640,480), (1024,768), (1280,1024)]
        self.qindex  = 1

        # location to save to.
        self.dest    = 'C:/Windows/Temp/dat_fosclg.tmp'

        # some preparations. get metrics and create device context.
        self.get_metrics()


    def get_metrics(self):
        # determine the resolution by pixel
        self.width  = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        self.height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        self.bottom = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        self.top    = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    def snap(self):
        # get foreground window handle
        self.hdesktop   = win32gui.GetDesktopWindow()

        # establish device context
        self.desktop_dc = win32gui.GetWindowDC(self.hdesktop)
        self.img_dc     = win32ui.CreateDCFromHandle(self.desktop_dc)

        # establish the device context saved in memory
        self.mem_dc     = self.img_dc.CreateCompatibleDC()

        # create bitmap object
        self.screenshot = win32ui.CreateBitmap()
        self.screenshot.CreateCompatibleBitmap(self.img_dc, self.width, self.height)
        self.mem_dc.SelectObject(self.screenshot)

        # copy the content of the screen to the device context saved in memory
        self.mem_dc.BitBlt((0,0), (self.width, self.height), self.img_dc, (self.bottom, self.top), win32con.SRCCOPY)

        # save the bitmap as a new file.
        self.screenshot.SaveBitmapFile(self.mem_dc, self.dest)

    def release(self):
        # release the object
        self.mem_dc.DeleteDC()
        win32gui.DeleteObject(self.screenshot.GetHandle())


    def convert(self):
        # convert bmp to jpg. bmp image file is too large.
        self.im = Image.open(self.dest)
        self.im.thumbnail(self.quality[self.qindex], Image.ANTIALIAS)
        self.im.save(self.dest, 'JPEG')


    def Start(self):
        # snap and save.
        self.snap()
        self.convert()

        # release the object.
        self.release()
