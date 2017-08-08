#!/usr/bin/env python
# -*- coding: utf-8 -*-
#======================================================================
#
# netstream.py - network data stream operation interface
#
# NOTE: The Replacement of TcpClient 
#
#======================================================================

import socket
import select
import struct
import time
import sys
import errno


#======================================================================
# RC4 cryption
#======================================================================
class rc4crypt(object):
    def __init__ (self, key = ''):
        self._key = key
        box = [ x for x in xrange(256) ]
        x = y = 0
        if len(key) > 0:
            for i in xrange(256):
                x = (x + box[i] + ord(key[i % len(key)])) & 255
                box[i], box[x] = box[x], box[i]
            x = y = 0
        self._box = box
        self._x = x
        self._y = y
    def crypt (self, data):
        box = self._box
        x, y = self._x, self._y
        if len(self._key) == 0:
            return data
        out = []
        for ch in data:
            x = (x + 1) & 255
            y = (y + box[x]) & 255
            box[x], box[y] = box[y], box[x]
            out.append(chr(ord(ch) ^ box[(box[x] + box[y]) & 255]))
        self._x, self._y = x, y
        return ''.join(out)


#======================================================================
# format of headers
#======================================================================
HEAD_WORD_LSB           = 0    # 2 bytes little endian (x86)
HEAD_WORD_MSB           = 1    # 2 bytes big endian (sparc)
HEAD_DWORD_LSB          = 2    # 4 bytes little endian (x86)
HEAD_DWORD_MSB          = 3    # 4 bytes big endian (sparc)
HEAD_BYTE_LSB           = 4    # 1 byte little endian
HEAD_BYTE_MSB           = 5    # 1 byte big endian
HEAD_WORD_LSB_EXCLUDE   = 6    # 2 bytes little endian, exclude itself
HEAD_WORD_MSB_EXCLUDE   = 7    # 2 bytes big endian, exclude itself
HEAD_DWORD_LSB_EXCLUDE  = 8    # 4 bytes little endian, exclude itself
HEAD_DWORD_MSB_EXCLUDE  = 9    # 4 bytes big endian, exclude itself
HEAD_BYTE_LSB_EXCLUDE   = 10   # 1 byte little endian, exclude itself
HEAD_BYTE_MSB_EXCLUDE   = 11   # 1 byte big endian, exclude itself
HEAD_DWORD_LSB_MASK     = 12   # 4 bytes little endian (x86) with mask
HEAD_RAW                = 13   # raw message

HEAD_HDR = (2, 2, 4, 4, 1, 1, 2, 2, 4, 4, 1, 1, 0, 0)
HEAD_INC = (0, 0, 0, 0, 0, 0, 2, 2, 4, 4, 1, 1, 0, 0)
HEAD_FMT = ('<H', '>H', '<I', '>I', '<B', '>B')

NET_STATE_STOP = 0              # state: init value
NET_STATE_CONNECTING = 1        # state: connecting
NET_STATE_ESTABLISHED = 2       # state: connected


#======================================================================
# netstream - basic tcp stream
#======================================================================
class netstream(object):

    def __init__(self, head = HEAD_WORD_LSB):
        self.sock = None        # socket object
        self.send_buf = ''      # send buffer
        self.recv_buf = ''      # recv buffer
        self.state = NET_STATE_STOP
        self.errd = ( errno.EINPROGRESS, errno.EALREADY, errno.EWOULDBLOCK )
        self.conn = ( errno.EISCONN, 10057, 10053 )
        self.errc = 0
        self.headmsk = False
        self.headraw = False
        self.__head_init(head)
        self.crypts = None
        self.cryptr = None
        self.ipv6 = False
        self.eintr = ()
        if 'EINTR' in errno.__dict__:
            self.eintr = (errno.__dict__['EINTR'],)
        self.block = False
    
    def __head_init(self, head):
        self.headmsk = False
        self.headraw = False
        if head == HEAD_DWORD_LSB_MASK:
            head = HEAD_DWORD_LSB
            self.headmsk = True
        if (head < 0) or (head > 13): head = 0
        mode = head % 6
        self.__head_mode = head
        self.__head_hdr = HEAD_HDR[head]
        self.__head_inc = HEAD_INC[head]
        self.__head_fmt = HEAD_FMT[mode]
        self.__head_int = mode
        if head == 13:
            self.headraw = True
        return 0

    def __try_connect(self):
        if (self.state == NET_STATE_ESTABLISHED):
            return 1
        if (self.state != NET_STATE_CONNECTING):
            return -1
        try:
            self.sock.recv(0)
        except socket.error, e:
            if e.errno in self.conn:
                return 0
            if e.errno in self.errd:
                self.state = NET_STATE_ESTABLISHED
                self.recv_buf = ''
                return 1
            #sys.stderr.write('[TRYCONN] '+strerror+'\n')
            self.close()
            return -1
        self.state = NET_STATE_ESTABLISHED
        return 1

    # try to receive all the data into recv_buf
    def __try_recv(self):
        rdata = ''
        while 1:
            text = ''
            try:
                text = self.sock.recv(1024)
                if not text:
                    self.errc = 10000
                    self.close()
                    return -1
            except socket.error, e:
                if not e.errno in self.errd:
                    #sys.stderr.write('[TRYRECV] '+strerror+'\n')
                    self.errc = e.errno
                    self.close()
                    return -1
            if text == '':
                break
            if self.cryptr:
                text = self.cryptr.crypt(text)
            rdata += text
        self.recv_buf += rdata
        return len(rdata)

    # send data from send_buf until block (reached system buffer limit)
    def __try_send(self):
        wsize = 0
        if (len(self.send_buf) == 0):
            return 0
        try:
            wsize = self.sock.send(self.send_buf)
        except socket.error, e:
            if not e.errno in self.errd:
                #sys.stderr.write('[TRYSEND] '+strerror+'\n')
                self.errc = e.errno
                self.close()
                return -1
        self.send_buf = self.send_buf[wsize:]
        return wsize

    # connect the remote server
    def connect(self, address, port, head = -1, block = False, timeout = 0):
        self.close()
        self.block = block
        af = socket.AF_INET
        if ':' in address:
            if not 'AF_INET6' in socket.__dict__:
                return -1
            if not socket.has_ipv6:
                return -2
            af = socket.AF_INET6
            self.ipv6 = True
        self.sock = socket.socket(af, socket.SOCK_STREAM)
        to = self.sock.gettimeout()
        if not self.block:
            self.sock.setblocking(0)
        elif timeout > 0:
            self.sock.settimeout(timeout)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.state = NET_STATE_CONNECTING
        try:
            hr = self.sock.connect_ex((address, port))
        except socket.error, e:
            if self.block:
                self.close()
                return -3
        if self.block and hr != 0:
            return -4
        if self.block and timeout > 0:
            self.sock.settimeout(to)
        self.send_buf = ''
        self.recv_buf = ''
        self.errc = 0
        if head >= 0 and head <= 13:
            self.__head_init(head)
        if self.block:
            self.state = NET_STATE_ESTABLISHED
        return 0

    # close connection
    def close(self):
        self.state = NET_STATE_STOP
        if not self.sock:
            return 0
        try:
            self.sock.close()
        except:
            pass
        self.sock = None
        self.crypts = None
        self.cryptr = None
        self.ipv6 = False
        self.block = False
        return 0
    
    # assign a socket to netstream
    def assign(self, sock, head = -1, block = False):
        self.close()
        self.block = block
        self.sock = sock
        self.sock.setblocking(self.block and 1 or 0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.state = NET_STATE_ESTABLISHED
        if head >= 0 and head <= 13:
            self.__head_init(head)
        self.send_buf = ''
        self.recv_buf = ''
        return 0
    
    # update 
    def process(self):
        if (self.state == NET_STATE_STOP) or (self.block):
            return 0
        if self.state == NET_STATE_CONNECTING:
            self.__try_connect()
        if self.state == NET_STATE_ESTABLISHED:
            self.__try_recv()
        if self.state == NET_STATE_ESTABLISHED:
            self.__try_send()
        return 0

    # return state
    def status(self):
        return self.state
    
    # get errno
    def error(self):
        return self.errc
    
    # append data to send_buf then try to send it out (__try_send)
    def __send_raw(self, data):
        if self.block:
            if self.state == NET_STATE_ESTABLISHED:
                try: 
                    self.sock.sendall(data)
                except socket.error, e:
                    self.close()
                    return -1
            return 0
        self.send_buf += data
        self.process()
        return 0
    
    # peek data from recv_buf (read without delete it)
    def __peek_raw(self, size):
        self.process()
        if len(self.recv_buf) == 0:
            return ''
        if size > len(self.recv_buf):
            size = len(self.recv_buf)
        rdata = self.recv_buf[0:size]
        return rdata
    
    # read data from recv_buf (read and delete it from recv_buf)
    def __recv_raw(self, size):
        rdata = self.__peek_raw(size)
        size = len(rdata)
        self.recv_buf = self.recv_buf[size:]
        return rdata
    
    # receive all data
    def __recv_all(self, size):
        rdata = ''
        if (size < 1) or (self.sock == None):
            return ''
        while 1:
            text = ''
            try: 
                text = self.sock.recv(size)
            except socket.error, e:
                if (e.errno in self.eintr): continue
                return rdata
            if len(text) == 0:
                self.close()
                return rdata
            rdata += text
            size = size - len(text)
            if (size <= 0): break
        return rdata

    # receive in blocking mode
    def __block_recv(self):
        if self.state != NET_STATE_ESTABLISHED:
            return None
        if self.headraw:
            text = ''
            try: 
                text = self.sock.recv(0x1000)
            except socket.error, e:
                if not (e.errno in self.eintr): 
                    self.close()
                    return None
                return rdata
            return text
        rsize = self.__recv_all(self.__head_hdr)
        if len(rsize) < self.__head_hdr:
            self.close()
            return None
        size = struct.unpack(self.__head_fmt, rsize)[0] + self.__head_inc
        data = self.__recv_all(size - self.__head_hdr)
        if len(data) + self.__head_hdr < size:
            self.close()
            return None
        return data
    
    # append data into send_buf with a size header
    def send(self, data, category = 0):
        size = len(data) + self.__head_hdr - self.__head_inc
        if self.headmsk:
            if category < 0: category = 0
            if category > 255: category = 255
            size = (category << 24) | size
        wsize = struct.pack(self.__head_fmt, size)
        packet = wsize + data
        if self.headraw:
            packet = data
        if self.crypts:
            packet = self.crypts.crypt(packet)
        return self.__send_raw(packet)
    
    # recv an entire message from recv_buf
    def recv(self):
        if self.block:
            return self.__block_recv()
        if self.headraw:
            return self.__recv_raw(len(self.recv_buf))
        rsize = self.__peek_raw(self.__head_hdr)
        if (len(rsize) < self.__head_hdr):
            return ''
        size = struct.unpack(self.__head_fmt, rsize)[0] + self.__head_inc
        if (len(self.recv_buf) < size):
            return ''
        self.__recv_raw(self.__head_hdr)
        return self.__recv_raw(size - self.__head_hdr)

    # set tcp nodelay flag
    def nodelay (self, nodelay = 0):
        if not 'TCP_NODELAY' in socket.__dict__:
            return -1
        if self.state != NET_STATE_ESTABLISHED:
            return -2
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, nodelay)
        return 0
    
    # set tcp keepalive
    def keepalive (self, keepalive = 0):
        if not 'SO_KEEPALIVE' in socket.__dict__:
            return -1
        if self.sock == None:
            return -2
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, keepalive)
        except:
            return -3
        return 0
    
    # set rc4 key for sending encryption
    def setskey (self, rc4key = ''):
        if not rc4key:
            self.crypts = None
        else:
            self.crypts = rc4crypt(rc4key)
        return 0
    
    # set rc4 key for recving decryption
    def setrkey (self, rc4key = ''):
        if not rc4key:
            self.cryptr = None
        else:
            self.cryptr = rc4crypt(rc4key)
        return 0
    
    # set timeout
    def settimeout (self, seconds):
        if self.sock == None:
            return False
        try:
            self.sock.settimeout(seconds)
        except:
            return False
        return True
    
    # get timeout
    def gettimeout (self):
        if self.sock == None:
            return 0
        try:
            return self.sock.gettimeout()
        except:
            pass
        return 0


#======================================================================
# nethost - basic tcp host
#======================================================================
NET_NEW =       0   # new connection��(id,tag) ip/d,port/w   <hid>
NET_LEAVE =     1   # lost connection��(id,tag)         <hid>
NET_DATA =      2   # data comming��(id,tag) data...    <hid>
NET_TIMER =     3   # timer event: (none, none) 


#======================================================================
# nethost - basic tcp host
#======================================================================
class nethost(object):

    def __init__ (self, head = HEAD_WORD_LSB):
        self.host = 0
        self.state = 0
        self.clients = []
        self.index = 1
        self.queue = []
        self.count = 0
        self.sock = 0
        self.port = 0
        self.head = head
        self.timeout = 70.0
        self.timeslap = long(time.time() * 1000)
        self.period = 0
    
    # start listenning
    def startup(self, port = 0):
        self.shutdown()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try: self.sock.bind(('0.0.0.0', port))
        except: 
            try: self.sock.close()
            except: pass
            return -1
        self.sock.listen(65536)
        self.sock.setblocking(0)
        self.port = self.sock.getsockname()[1]
        self.state = 1
        self.timeslap = long(time.time() * 1000)
        return 0

    # shutdown service
    def shutdown(self):
        if self.sock: 
            try: self.sock.close()
            except: pass
        self.sock = 0
        self.index = 1
        for n in self.clients:
            if not n: continue
            try: n.close()
            except: pass
        self.clients = []
        self.queue = []
        self.state = 0
        self.count = 0
    
    # private: close hid
    def __close(self, hid, code = 0):
        pos = hid & 0xffff
        if (pos < 0) or (pos >= len(self.clients)): return -1
        client = self.clients[pos]
        if client == None: return -2
        if client.hid != hid: return -3
        client.close()
        return 0
    
    def __send(self, hid, data):
        pos = hid & 0xffff
        if (pos < 0) or (pos >= len(self.clients)): return -1
        client = self.clients[pos]
        if client == None: return -2
        if client.hid != hid: return -3
        client.send(data)
        client.process()
        return 0

    # update: process clients and handle accepting
    def process(self):
        current = time.time()
        if self.state != 1: return 0
        sock = None
        try: 
            sock, remote = self.sock.accept()
            sock.setblocking(0)
        except: pass
        if self.count >= 0x10000:
            try: sock.close()
            except: pass
            sock = None
        if sock:
            pos = -1
            for i in xrange(len(self.clients)):
                if self.clients[i] == None:
                    pos = i
                    break
            if pos < 0:
                pos = len(self.clients)
                self.clients.append(None)
            hid = (pos & 0xffff) | (self.index << 16)
            self.index += 1
            if self.index >= 0x7fff: self.index = 1
            client = netstream(self.head)
            client.assign(sock, self.head)
            client.hid = hid
            client.tag = 0
            client.active = current
            client.peername = sock.getpeername()
            self.clients[pos] = client
            self.count += 1
            self.queue.append((NET_NEW, hid, 0, repr(client.peername)))
        for pos in xrange(len(self.clients)):
            client = self.clients[pos]
            if not client: continue
            client.process()
            while client.status() == 2:
                data = client.recv()
                if data == '': break
                self.queue.append((NET_DATA, client.hid, client.tag, data))
                client.active = current
            timeout = current - client.active
            if (client.status() == 0) or (timeout >= self.timeout):
                hid, tag = client.hid, client.tag
                self.queue.append((NET_LEAVE, hid, tag, ''))
                self.clients[pos] = None
                client.close()
                del client
                self.count -= 1
        current = long(time.time() * 1000)
        if current - self.timeslap > 100000:
            self.timeslap = current
        period = self.period
        if period > 0:
            while self.timeslap < current:
                self.queue.append((NET_TIMER, 0, 0, ''))
                self.timeslap += period
        return 0

    # send data to hid
    def send(self, hid, data):
        return self.__send(hid, data)
    
    # close client
    def close(self, hid):
        return self.__close(hid, hid)
    
    # set tag
    def settag(self, hid, tag = 0):
        pos = hid & 0xffff
        if (pos < 0) or (pos >= len(self.clients)): return -1
        client = self.clients[pos]
        if client == None: return -2
        if hid != client.hid: return -3
        client.tag = tag
        return 0
    
    # get tag
    def gettag(self, hid):
        pos = hid & 0xffff
        if (pos < 0) or (pos >= len(self.clients)): return -1
        client = self.clients[pos]
        if client == None: return -1
        if hid != client.hid: return -1
        return client.tag
    
    # read event
    def read(self):
        if len(self.queue) == 0:
            return (-1, 0, 0, '')
        event = self.queue[0]
        self.queue = self.queue[1:]
        return event
    
    def settimer(self, millisec = 1000):
        if millisec <= 0: 
            millisec = 0
        self.period = millisec
        self.timeslap = long(time.time() * 1000)

    def nodelay (self, hid, nodelay = 0):
        pos = hid & 0xffff
        if (pos < 0) or (pos >= len(self.clients)): return -1
        client = self.clients[pos]
        if client == None: return -1
        if hid != client.hid: return -1
        return client.nodelay(nodelay)



#----------------------------------------------------------------------
# instructions
#----------------------------------------------------------------------
ITMT_NEW    =   0   # �½��ⲿ���ӣ�(id,tag) ip/d,port/w
ITMT_LEAVE  =   1   # �Ͽ��ⲿ���ӣ�(id,tag)
ITMT_DATA   =   2   # �ⲿ���ݵ��(id,tag) data...
ITMT_CHANNEL=   3   # Ƶ��ͨ�ţ�(channel,tag)
ITMT_CHNEW  =   4   # Ƶ��������(channel,id)
ITMT_CHSTOP =   5   # Ƶ���Ͽ���(channel,tag)
ITMT_SYSCD =    6   # ϵͳ��Ϣ��(subtype, v) data...
ITMT_TIMER  =   7   # ϵͳʱ�ӣ�(timesec,timeusec)
ITMT_NOOP   =   8   # ��ָ�(wparam, lparam)
ITMT_UNRDAT =   10  # ���ɿ����ݰ���(id,tag)

ITMC_DATA   =   0   # �ⲿ���ݷ��ͣ�(id,*) data...
ITMC_CLOSE  =   1   # �ر��ⲿ���ӣ�(id,*)
ITMC_TAG    =   2   # ����TAG��(id,tag)
ITMC_CHANNEL=   3   # ���ͨ�ţ�(channel,*) data...
ITMC_MOVEC  =   4   # �ƶ��ⲿ���ӣ�(channel,id) data...
ITMC_SYSCD  =   5   # ϵͳ�������ݣ�(subtype, v) data...
ITMC_BROADCAST =6
ITMC_NOOP   =   7   # ��ָ�(*,*)
ITMC_UNRDAT =   10  # ���ɿ����ݰ���(id,tag)

ITMS_CONNC =        0    # ������������(st,0) cu/d,cc/d
ITMS_LOGLV =        1    # ������־����(st,level)
ITMS_LISTC =        2    # ����Ƶ����Ϣ(st,cn) d[ch,id,tag],w[t,c]
ITMS_RTIME =        3    # ϵͳ����ʱ��(st,wtime)
ITMS_TMVER =        4    # ����ģ��汾(st,tmver)
ITMS_REHID =        5    # ����Ƶ����(st,ch)
ITMS_QUITD =        6    # �����Լ��˳�
ITMS_TIMER =        8    # ����Ƶ�����ʱ��(st,timems)
ITMS_INTERVAL =        9    # �����Ƿ�Ϊ���ģʽ(st,isinterval)
ITMS_FASTMODE =        10    # �����Ƿ����ÿ���ģʽ
ITMS_CHID       = 11
ITMS_BOOKADD    = 12    # ���Ӷ���
ITMS_BOOKDEL    = 13    # ȡ������
ITMS_BOOKRST    = 14    # ��ն���
ITMS_RC4SKEY    = 16    # ���÷���KEY (st, hid) key
ITMS_RC4RKEY    = 17    # ���ý���KEY (st, hid) key


#----------------------------------------------------------------------
# CCLIB
#----------------------------------------------------------------------
class CCLIB (object):

    def __init__ (self):
        self.ns = netstream()
        self.attached = False
        self.chid = -1
    
    def attach (self, ip, port, head, channel, timeout = 0):
        self.attached = False
        if self.ns.connect(ip, port, head, True, timeout) != 0:
            return False
        self.ns.send(struct.pack('<H', channel))
        self.write(ITMC_SYSCD, ITMS_CHID, 0, '')
        event, wparam, lparam, data = self.read()
        if event != ITMT_SYSCD or wparam != ITMS_CHID:
            self.ns.close()
            return False
        self.chid = lparam
        self.attached = True
        return True
    
    def detach (self, timeout = 0):
        if self.attached:
            if timeout <= 0: 
                timeout = 3.0
            self.write(ITMC_SYSCD, ITMS_QUITD, 0)
            if self.ns.sock:
                self.ns.sock.settimeout(timeout)
            ts = time.time()
            while time.time() - ts <= timeout + 0.4:
                x = self.read()
                if x[0] == None:
                    break
                if self.ns.state != NET_STATE_ESTABLISHED:
                    break
        self.ns.close()
        self.attached = False
    
    def write (self, event, wparam, lparam, data = ''):
        self.ns.send(struct.pack('<HII', event, wparam, lparam) + data)
    
    def read (self):
        pkt = self.ns.recv()
        if pkt == None or len(pkt) < 10:
            return None, -1, -1, ''
        event, wparam, lparam = struct.unpack('<HII', pkt[:10])
        data = pkt[10:]
        return event, wparam, lparam, data
    
    def send(self, hid, data):
        return self.write(ITMC_DATA, hid, 0, data)
    
    def close(self, hid, why):
        return self.write(ITMC_CLOSE, hid, why)

    def tag(self, hid, tag):
        return self.write(ITMC_TAG, hid, tag)

    def channel(self, ch, data):
        return self.write(ITMC_CHANNEL, ch, 0, data)

    def movec(self, ch, hid):
        return self.write(ITMC_MOVEC, ch, hid)

    def syscmd(self, cmd, param):
        return self.write(ITMC_SYSCD, cmd, param)

    def settimer(self, timeval):
        return self.syscmd(ITMS_TIMER, timeval)

    def setinterval(self, interval = False):
        return self.syscmd(ITMS_INTERVAL, interval)

    def setlogmask(self, mask):
        return self.syscmd(ITMS_LOGLV, mask)
    
    def groupcast (self, hids, data):
        pack = struct.pack
        lst = ''.join([ pack('<I', hid) for hid in hids ])
        return self.write(ITMC_BROADCAST, len(hids), 0, data + lst)
    
    def bookadd (self, category):
        return self.write(ITMC_SYSCD, ITMS_BOOKADD, category)
    
    def bookdel (self, category):
        return self.write(ITMC_SYSCD, ITMS_BOOKDEL, category)
    
    def bookrst (self):
        return self.write(ITMC_SYSCD, ITMS_BOOKRST, 0)
    
    def rc4_set_skey (self, hid, key):
        return self.write(ITMC_SYSCD, ITMS_RC4SKEY, hid, key)

    def rc4_set_rkey (self, hid, key):
        return self.write(ITMC_SYSCD, ITMS_RC4RKEY, hid, key)


#----------------------------------------------------------------------
# psyco speedup
#----------------------------------------------------------------------
def _psyco_speedup():
    try:
        import psyco
        psyco.bind(rc4crypt)
        psyco.bind(netstream)
        psyco.bind(nethost)
        psyco.bind(CCLIB)
    except:
        return False
    return True

_psyco_speedup()


#----------------------------------------------------------------------
# telnet server
#----------------------------------------------------------------------
class TelnetServer(object):
    def __init__(self, func, intro = None):
        self._port = None
        self._host = None
        self._intro = intro
        self._func = func
        self._server = nethost(13)
        self._data = { }

    def _try_get_input(self, hid, data):
        if data.find("\n") >= 0:
            cdata = self._data[hid]
            cdata.append(data)
            elements = "".join(cdata).split("\n")
            if len(elements[-1]) > 0:
                self._data[hid] = [ elements[-1], ]
            else:
                self._data[hid] = [ ]
            return [ e.strip() for e in elements[:-1] if len(e.strip()) ]
        else:
            self._data[hid].append(data)
            return [ ]

    def _send(self, hid, resp):
        self._server.send(hid, resp+"\n")
        self._server.process()

    def start(self, port, host="127.0.0.1"):
        self._data = { }
        self._host = host
        self._port = port
        self._server.startup(self._port)

    def shutdown(self):
        self._server.shutdown()

    def process(self):
        self._server.process()
        event, wparam, lparam, data = self._server.read()
        if event < 0: 
            return
        if event == NET_DATA:
            commands = self._try_get_input(wparam, data)
            for cmd in commands:
                resp = self._func(cmd)
                if resp:
                    self._send(wparam, resp)
        elif event == NET_NEW:
            self._data[wparam] = [ ]
            self._server.settag(wparam, wparam)
            self._server.nodelay(wparam, 1)
            if self._intro:
                self._server.send(wparam, self._intro(data))
        elif event == NET_LEAVE:
            try:
                del self._data[wparam]
            except: pass



#----------------------------------------------------------------------
# testing case
#----------------------------------------------------------------------
if __name__ == '__main__':
    host = nethost(8)
    host.startup(2000)
    sock = netstream(8)
    last = time.time()
    sock.connect('127.0.0.1', 2000)
    sock.send('Hello, world !!')
    stat = 0
    last = time.time()
    print 'service startup at port', host.port
    host.settimer(5000)
    sock.nodelay(0)
    sock.nodelay(1)
    while 1:
        time.sleep(0.1)
        host.process()
        sock.process()
        if stat == 0:
            if sock.status() == 2:
                stat = 1
                sock.send('Hello, world !!')
                last = time.time()
        elif stat == 1:
            if time.time() - last >= 3.0:
                sock.send('VVVV')
                stat = 2
        elif stat == 2:
            if time.time() - last >= 5.0:
                sock.send('exit')
                stat = 3
        event, wparam, lparam, data = host.read()
        if event < 0: continue
        print 'event=%d wparam=%xh lparam=%xh data="%s"'%(event, wparam, lparam, data)
        if event == NET_DATA:
            host.send(wparam, 'RE: ' + data)
            if data == 'exit': 
                print 'client request to exit'
                host.close(wparam)
        elif event == NET_NEW:
            host.send(wparam, 'HELLO CLIENT %X'%(wparam))
            host.settag(wparam, wparam)
            host.nodelay(wparam, 1)



