from crypto.AES import file_cipher
import os
import socket


class f_handler(object):

    def __init__(self):
        # get an instance of file_cipher.
        self._file_cipher = file_cipher()


    def download(self, socket_fh, savepath, password):
        # clear info and buffer.
        self.file_len_all = 0
        self.file_buffer  = ''

        # receive file size first.
        self.file_len_all = int(socket_fh.recv(16))
        print "[*] Downloading %d bytes to the local host..." % self.file_len_all

        # keep receiving and writing until filesize match.
        # remember to use flush(), or the chunk will be left behind in the memory, forever!
        self.fd = open(savepath + '.tmp', 'w+b')

        while self.check_filesize(self.fd, self.file_len_all) != 0:
            # check if the filesizes match. if not, keep receiving.
            # if both match, break loop and decrypt.
            self.file_buffer = socket_fh.recv(1024)
            if self.file_buffer:
                self.fd.write(self.file_buffer)
                self.fd.flush()
            else:
                # filesizes not match, and no data received.
                # we should wait a little longer.
                continue
        self.fd.close()

        # decrypt the file after downloading.
        self._file_cipher.dec_file(savepath + '.tmp', savepath, password)

        # remove temp file.
        os.remove(savepath + '.tmp')
        print "[+] The file has been downloaded to: %s\n" % savepath


    def upload(self, socket_fh, targetpath, password):
        # encrypt the target file before uploading.
        self._file_cipher.enc_file(targetpath, targetpath + '.tmp', password)

        # we will work on the temp file from now onf_handleronf_handler.
        targetpath = targetpath + '.tmp'

        # clear info and buffer.
        self.file_len_cur = 0
        self.file_len_all = 0
        self.file_buffer  = ''

        # get file size and send it.
        self.fd = open(targetpath, 'r+b')
        self.fd.seek(0,2)
        self.file_len_all = self.fd.tell()
        self.fd.seek(0,0)

        # upload the first block.
        socket_fh.send(str(self.file_len_all))
        print "[*] Uploading %d bytes to the remote host..." % self.file_len_all

        # keep reading and uploading until the end of the file.
        while self.file_len_cur < self.file_len_all:
            self.file_buffer  += self.fd.read(1024)
            socket_fh.send(self.file_buffer)
            self.file_len_cur += 1024
            self.file_buffer = ""
        self.fd.close()

        # remove temp file.
        os.remove(targetpath)
        print "[+] The file has been uploaded to: %s\n" % targetpath[:-4]


    def check_filesize(self, fd, filesize_correct):
        # remember the original fd position.
        self.temp_pos = self.fd.tell()

        # now traverse through the file and get filesize.
        self.fd.seek(0,2)
        self.filesize = self.fd.tell()

        # restore fd position.
        self.fd.seek(self.temp_pos,0)

        if self.filesize == filesize_correct:
            return 0
        else:
            return -1
