#!/usr/bin/env python3
"""
ExaBGP HTTP API

This is a hacky solution to allow a remote process (eabgpmon) to make calls to ExaBGP
It should eventually be replaced with reading to/from a named pipe or something using
a queue handler (RabbitMQ, Redis, etc.)

Receives an HTTP POST with a command and prints it to the STDIN process ExaBGP is
reading. Does no sort of validation or response checking from ExaBGP.

"""

import cgi
import http.server
import socketserver
from sys import stdout
import os
import ipaddress

PORT = 5001


class ServerHandler(http.server.SimpleHTTPRequestHandler):

    def createResponse(self, command):
        """ Send command string back as confirmation """
        self.send_response(200)
        self.send_header('Content-Type', 'application/text')
        self.end_headers()
        self.wfile.write(command.encode())
        self.wfile.flush()

    def do_POST(self):
        """ Process command from POST and output to STDOUT """
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'})
        command = form.getvalue('command')
        try:
            if not command:
                command = 'missing command key'
                raise ValueError
            action = command[:1]  # "+"=announce , "-"=withdraw
            ip = ipaddress.ip_network(command[1:])  # IP in CIDR notation (e.g 1.1.1.1/32)
            if action in ('+', '-'):
                message = '{} route {} next-hop {}\n'.format(
                    'announce' if action == '+' else 'withdraw', ip, os.environ['BGP_LOCAL'])
                stdout.write(message)
                stdout.flush()
                self.createResponse('Success: %s' % message)
            else:
                raise ValueError
        except ValueError:
            stdout.write(command)
            stdout.flush()
            self.createResponse("""Failure: invalid syntax '%s'
            Correct syntax: <+-><IP/MASK>
            e.g.:
            command=\"+1.1.1.1/32\" or
            command=\"-20.20.20.0/24\"
            """ % command)


handler = ServerHandler
httpd = socketserver.TCPServer(('', PORT), handler)
stdout.write('serving at port %s\n' % PORT)
stdout.flush()
httpd.serve_forever()
