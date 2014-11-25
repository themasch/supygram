###
# Copyright (c) 2014, Mark Schmale <masch@masch.it>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import supybot.log as log
from threading import Thread
from pytg.Connection import TelegramConnection
import sys
import shutil
import hashlib
import inspect
import os
import stat
import ConfigParser

def stripCommand(str):
    if len(str) == 0:
        return str
    if str[0] == "!":
        position = str.find(' ')
    if position < 0:
        return ""
    return str[position + 1:]


def start_client(connection):
    connection.loop()


class Supygram(callbacks.Plugin):
    """Add the help for "@plugin help Telegram" here
    This should describe *how* to use this plugin."""
    threaded = True

    def __init__(self, irc):
        callbacks.Plugin.__init__(self, irc)
        self.irc = irc
        self.connection = TelegramConnection("localhost", 9012)
        self.thread = Thread(target=start_client, args=(self.connection, ))
        self.thread.start()
        self.connection.start_main_session()
        self.connection.on_message(self.publish_msg)
        self.connection.on_picture(self.publish_picture)
        self.ignoreList = []
        self.lastPictureSender = False
        self.config = ConfigParser.RawConfigParser()
        self.config.read(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/supygram.conf")
        self.ignoreList.append(self.config.get("global", "bot_nick"))


    def die(self):
        self.connection.close()
        self.thread.join()
        callbacks.Plugin.die(self)
        del sys.modules['supygram.pytg.Connection']
        del sys.modules['supygram.pytg.Message']

    def publish_picture(self, path):
        filename = hashlib.md5(open(path, 'rb').read()).hexdigest() + ".jpg"
        dst = self.config.get("global", "pic_dir") + filename
        shutil.move(path, dst)
        os.chmod(dst, stat.S_IROTH)
        self.irc.queueMsg(ircmsgs.privmsg(self.config.get("global", "channel"), self.lastPictureSender + ": " + self.config.get("global", "url_prefix") + filename))
         
    def publish_msg(self, msg):
        text = "<{0}> {1}".format(msg.sender, msg.message)
        print "incoming message"
        if msg.sender not in self.ignoreList:
            if msg.message == "[photo]":
                self.connection.load_photo(msg.msgid)
                self.lastPictureSender = msg.sender
            else:
                self.irc.queueMsg(ircmsgs.privmsg(self.config.get("global", "channel"), text))

    def t(self, irc, msg, args):
        if msg.command == 'PRIVMSG' and ircutils.isChannel(msg.args[0]):
            if self.registryValue('group', msg.args[0]):
                channel = self.registryValue('group', msg.args[0])
                text = "{0}: {1}".format(msg.nick, stripCommand(msg.args[1]))
                self.connection.msg(channel, text)
        

Class = Supygram 


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
