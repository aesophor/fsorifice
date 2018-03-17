from screenlogger   import fso_screenlogger
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import pymjpeg
import time
import sys
import os


class vnchandler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        # Response headers (multipart)
        for k, v in pymjpeg.request_headers().items():
            self.send_header(k, v)

        # Multipart content
        while True:
            try:
                # capture a new screen.
                _screenlogger.Start()

                # Part boundary string
                self.end_headers()
                self.wfile.write(pymjpeg.boundary)
                self.end_headers()

                # Part headers
                for k, v in pymjpeg.image_headers(_screenlogger.dest).items():
                    self.send_header(k, v)
                self.end_headers()

                # Part binary
                for chunk in pymjpeg.image(_screenlogger.dest):
                    self.wfile.write(chunk)

                time.sleep(0.1)
            except Exception, self.e:
                print self.e
                break

    def log_message(self, format, *args):
        return


class fso_vnc(object):

    def __init__(self):
        pass

    def Start(self):
        httpd = HTTPServer(('', 8080), vnchandler)
        httpd.serve_forever()

_screenlogger = fso_screenlogger()
