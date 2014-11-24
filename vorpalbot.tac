#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser
from twisted.application import service
from twisted.words.protocols.jabber.jid import JID
from twisted.internet import task
from wokkel.client import XMPPClient
from wokkel import xmppim
from VorpalBot import VorpalBot

config = SafeConfigParser()
config.read("vorpal.conf")
# database
dbpath = config.get('DEFAULT', 'dbpath')
# Bot auth
jid = JID(config.get('DEFAULT', 'bot_jid'))
password = config.get('DEFAULT', 'bot_password')
room_jid = JID(config.get('DEFAULT', 'room_jid'))
nick = config.get('DEFAULT', 'bot_nick')

# Set up the Twisted application
application = service.Application("MUC Client")

client = XMPPClient(jid, password)
client.logTraffic = True
client.setServiceParent(application)

# send presence periodically to avoid server-side timeouts on c2s-connection
presence = xmppim.PresenceProtocol()
presence.setHandlerParent(client)
lookalive = task.LoopingCall(presence.available)
lookalive.start(600.0)

mucHandler = VorpalBot(room_jid, nick, dbpath)
mucHandler.setHandlerParent(client)
