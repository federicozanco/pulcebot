#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# PulceBot: a simple XMPP bot based on Sleek XMPP Library
Copyright (C) 2016  Federico Zanco, federico.zanco@gmail.com

## Based on
This file is based on echobot.py, original header:

SleekXMPP: The Sleek XMPP Library
Copyright (C) 2010  Nathanael C. Fritz
This file is part of SleekXMPP.

See the file LICENSE for copying permission.

## Use
```
$ python3 pulcebot.py -d -j pulcebot@dirtykid.com -p "pulcepassword"
```
### Options
- -d/--debug: prints debug messages;
- -j/--jid: JID to use;
- -p/--jid: password to use;
- -i/--pid: path where to save the process id;

## Chat commands
- help: prints a short help;
- ip: returns the external/WAN IP address;
- exec <command>: executes <command> and returns output (timeout = 60s);
- exect <timeout> <command>: executes <command> and returns output (timeout = <timeout>s)\n'
- ping: just ping the bot;

## get-wan-ip shell script example
```
#! /bin/bash

# Script:       get-wan-ip
# Use:          get-wan-ip
# Options:      none
# Provide:      Get node external ip. This is useful when the node is behind a nat.

wget -qO- http://checkip.dyndns.org | html2text | grep -e "Current IP Address:" | cut -c21-35
```

## cron check example
```
*/5 *   * * *   user    cd /path/to/pulcebot/ ; python3 pulcebot.py -j pulcebot@dirtykid.com -p "pulcepassword"
```

## License
This file is part of PulceBot.

PulceBot is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PulceBot; if not, If not, see <http://www.gnu.org/licenses/>.
"""

import subprocess
import shlex
import sys
import os
import psutil
import logging
import getpass
from optparse import OptionParser

import sleekxmpp

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


class PulceBot(sleekxmpp.ClientXMPP):

    """
    A simple SleekXMPP bot that will echo messages it
    receives, along with a short thank you message.
    """

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message)

    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        if msg['type'] in ('chat', 'normal'):
            # print('MESSAGE BODY = ' + msg['body'])

            tokens = msg['body'].split()
            cmd = tokens[0].lower()

            if cmd == 'help':
                help = '\n\nPulce Bot\'s HELP\n\n'
                help += 'help => shows this help\n'
                help += 'ip => returns the external/WAN IP address\n'
                help += 'exec <command> => exec <command> and returns output (timeout = 60s)\n'
                help += 'exect <timeout> <command> => exec <command> and returns output (timeout = <timeout>s)\n'
                help += 'ping => replays with pong. What did you expect?!\n'
                msg.reply(help).send()
            elif cmd == 'ip':
                try:
                    msg.reply(subprocess.check_output('get-wan-ip', timeout=60).decode('utf8')).send()
                except subprocess.TimeoutExpired as e:
                    msg.reply(msg['body'] + ' timeout').send()
            elif cmd == 'exect':
                try:
                    exec_timeout = int(tokens[1])
                    del tokens[:2]
                    cmd_to_exec = ' '.join(tokens)
                    msg.reply(subprocess.check_output(shlex.split(cmd_to_exec), stderr=subprocess.STDOUT, timeout=exec_timeout, shell=False).decode('utf8')).send()
                except subprocess.TimeoutExpired as e:
                    msg.reply(msg['body'] + ' timeout:\n\n' + e.output.decode('utf8')).send()
                except subprocess.CalledProcessError as e:
                    msg.reply(msg['body'] + ' error:\n\n' + e.output.decode('utf8')).send()
            elif cmd == 'exec':
                try:
                    del tokens[0]
                    cmd_to_exec = ' '.join(tokens)
                    msg.reply(subprocess.check_output(shlex.split(cmd_to_exec), stderr=subprocess.STDOUT, timeout=60, shell=False).decode('utf8')).send()
                except subprocess.TimeoutExpired as e:
                    msg.reply(msg['body'] + ' timeout:\n\n' + e.output.decode('utf8')).send()
                except subprocess.CalledProcessError as e:
                    msg.reply(msg['body'] + ' error:\n\n' + e.output.decode('utf8')).send()
            elif cmd == 'ping':
                msg.reply('pong').send()

if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid",
                    dest="jid", help="JID to use")
    optp.add_option("-p", "--password",
                    dest="password", help="password to use")

    # PID option
    optp.add_option("-i", "--pid",
                    dest="pid", help="PID file to use (default pulce_bot.pid)",
                    default="pulcebot.pid")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel, format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")

    # Check if PID file exists and if a process with the read PID is running
    if os.path.isfile(opts.pid):
        with open(opts.pid, "r+") as pid_file:
            saved = pid_file.read()
            if psutil.pid_exists(int(saved)):
                sys.exit()

    with open(opts.pid, "w") as pid_file:
         pid_file.write(str(os.getpid()))

    # Setup the EchoBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = PulceBot(opts.jid, opts.password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # If you are connecting to Facebook and wish to use the
    # X-FACEBOOK-PLATFORM authentication mechanism, you will need
    # your API key and an access token. Then you'll set:
    # xmpp.credentials['api_key'] = 'THE_API_KEY'
    # xmpp.credentials['access_token'] = 'THE_ACCESS_TOKEN'

    # If you are connecting to MSN, then you will need an
    # access token, and it does not matter what JID you
    # specify other than that the domain is 'messenger.live.com',
    # so '_@messenger.live.com' will work. You can specify
    # the access token as so:
    # xmpp.credentials['access_token'] = 'THE_ACCESS_TOKEN'

    # If you are working with an OpenFire server, you may need
    # to adjust the SSL version used:
    # xmpp.ssl_version = ssl.PROTOCOL_SSLv3

    # If you want to verify the SSL certificates offered by a server:
    # xmpp.ca_certs = "path/to/ca/cert"

    # Connect to the XMPP server and start processing XMPP stanzas.
    #if xmpp.connect(('talk.google.com', 5222)):
    if xmpp.connect():
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(block=True)
