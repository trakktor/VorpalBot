#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.words.protocols.jabber.jid import JID
from twisted.python import log
from wokkel.client import XMPPClient
from wokkel.muc import MUCClient
from datetime import datetime, timedelta
from MUCLogSqlite import MUCLogSqlite

class VorpalBot(MUCClient):
    def __init__(self, roomJID, nick, dbpath):
        MUCClient.__init__(self)
        self.roomJID = roomJID
        self.nick = nick
        self.muc_log = MUCLogSqlite(dbpath)

    def connectionInitialized(self):
        """
        Once authorized, join the room.
        """
        def joinedRoom(room):
            if room.locked:
                # Just accept the default configuration.
                return self.configure(room.roomJID, {})

        MUCClient.connectionInitialized(self)

        d = self.join(self.roomJID, self.nick)
        d.addCallback(joinedRoom)
        d.addCallback(lambda _: log.msg("Joined room"))
        d.addErrback(log.err, "Join failed")

    def receivedGroupChat(self, room, user, message):
        """
        Called when a groupchat message was received.
        """
        if user.nick <> self.nick:
            self.muc_log.log(user.nick, message.body)
        if message.body.startswith(self.nick + u":"):
            nick, text = nick, text = message.body.split(':', 1)
            text = text.strip().lower()
            if text == u"fetch":
                zeit = datetime.now()
                zeitdelta = timedelta(hours=4)
                blob = self.muc_log.fetch_last(zeit - zeitdelta)
                body = u"".join(map(lambda x: u"[{}] {}: {}\n".format(*x), blob))
                self.groupChat(self.roomJID, body)
