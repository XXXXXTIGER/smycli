#!/usr/bin/env python
# coding:utf8
'''Setup a secure tunnel use paramiko.
reference to some content from the internet'''
from __future__ import with_statement
from __future__ import absolute_import
import os
import socket
import select
import random
import sys
import paramiko
from multiprocessing import Process
try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer


__all__ = ["Forwarder"]
paramiko.util.log_to_file('forward.log')


class ForwardServer (SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class Handler (SocketServer.BaseRequestHandler):

    def handle(self):
        try:

            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   (self.chain_host,
                                                    self.chain_port),
                                                   self.request.getpeername())
        except Exception as e:
            print('Incoming request to %s:%d failed: %s' % (self.chain_host,
                                                            self.chain_port,
                                                            repr(e)))
            return
        if chan is None:
            print('Incoming request to %s:%d was rejected by the SSH server.' %
                  (self.chain_host, self.chain_port))
            return

        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        peername = self.request.getpeername()
        chan.close()
        self.request.close()


def forward_tunnel(local_host, local_port, remote_host, remote_port, ssh_host, ssh_port, ssh_user, pkey, password):

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    try:
        client.connect(ssh_host, ssh_port, username=ssh_user, key_filename=pkey,
                       look_for_keys=True, password=password)
        transport = client.get_transport()

        class SubHander (Handler):
            chain_host = remote_host
            chain_port = remote_port
            ssh_transport = transport
        ForwardServer((local_host, local_port), SubHander).serve_forever()
    except Exception as e:
        return 1, '*** Failed to connect to %s:%d: %r' % (ssh_host, ssh_port, e)
    finally:
        client.close()
        return 0, ''


class Forwarder(object):
    '''forward tcp connection via ssh tunnel
    example:        
        server = forwarder(
            ssh_host=host,
            ssh_port=ssh_port,
            ssh_username=ssh_username,
            ssh_private_key=ssh_pkey,
            ssh_password=ssh_password,
            local_bind_address=None,
            remote_bind_address=('127.0.0.1', port),
        )
        server.start()
        local_bind_host, local_bind_port = server.local_address()
        *****
        now you can access the `local_bind_host`, `local_bind_port` to secure the connection to remote server
        *****
        server.stop()
    '''

    def __init__(self, local_bind_address, remote_bind_address, ssh_host='localhost', ssh_port=22, ssh_username='root', ssh_password=None, ssh_private_key=None):

        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_user = ssh_username
        self.password = ssh_password
        self.pkey = ssh_private_key
        self.local_addr = local_bind_address
        self.remote_addr = remote_bind_address
        self.p = None

    def start(self):

        if self.local_addr is None:
            self.local_bind_host = ''
            self.local_bind_port = random.choice(range(2000, 65530))
        else:
            self.local_bind_host, self.local_bind_port = self.local_addr
        remote_host, remote_port = self.remote_addr

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy())
        client.connect(self.ssh_host, self.ssh_port, username=self.ssh_user, key_filename=self.pkey,
                       look_for_keys=True, password=self.password)
        transport = client.get_transport()
        self.p = Process(target=forward_tunnel, args=(self.local_bind_host,
                                                      self.local_bind_port, remote_host, remote_port, self.ssh_host, self.ssh_port, self.ssh_user, self.pkey, self.password)
                         )
        self.p.start()

    def stop(self):
        if isinstance(self.p, Process) and self.p.is_alive():
            try:
                self.p.terminate()
            except:
                pass

    def local_address(self):
        return self.local_bind_host, self.local_bind_port
