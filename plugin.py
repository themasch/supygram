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


class Telegram(callbacks.Plugin):
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

    def die(self):
        self.connection.close()
        self.thread.join()
        callbacks.Plugin.die(self)

    def publish_msg(self, msg):
        text = "<{0}> {1}".format(msg.sender, msg.message)
        self.irc.queueMsg(ircmsgs.privmsg("#maschbotdev", text))

    def teg(self, irc, msg, args):
        self.connection.msg("Church of Root", msg.nick + ": " + stripCommand(msg.args[1]))


Class = Telegram


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
