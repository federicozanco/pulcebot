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
