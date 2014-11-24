#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
sqlite3 logging driver
"""

# TODO:
# - log.user as foreing key on users.id/jid
# - output segmentation for huge output logs
# - FTS log table for search

import sqlite3
import datetime
from twisted.python import log
from twisted.internet import reactor


LOGDB_VERSION = u"alpha"
BEGINNING_OF_TIMES = datetime.datetime(1970,1,1)

class MUCLogSqlite:
    def __init__(self, dbpath):
        self.dbpath = dbpath # for reference only
        self.conn = sqlite3.connect(dbpath)
        """
        If we're still alive, we should have an sqlite base by now.
        DB either has consistent structure, or it's new -
         or it belongs to someone else.
        """
        c = self.conn.cursor()
        try:
            c.execute('''SELECT version FROM logdb_version''')
        except sqlite3.OperationalError:
            c.execute('''SELECT name FROM sqlite_master''')
            t = c.fetchall()
            if len(t) == 0:
                log.msg("Got empty database")
                self.initdb()
                return
            else:
                log.err("Possibly foreign database; terminating")
                reactor.stop()

        if c.fetchone() <> (LOGDB_VERSION,):
            log.err("Obsolete database format; please update")
            reactor.stop()
        log.msg("Existing database aquired")
        c.close()

    def initdb(self):
        """
        Initialize tables and stuff
        """
        log_t = '''CREATE TABLE log (time TEXT, user TEXT, message TEXT)'''
        users_t = '''CREATE TABLE users (
                        id INTEGER PRIMARY KEY,
                        jid TEXT,
                        last_leave TEXT,
                        last_join TEXT )'''
        version_t = '''CREATE TABLE logdb_version (version TEXT)'''
        version_r = '''INSERT INTO logdb_version VALUES (?)'''
        c = self.conn.cursor()
        c.execute( log_t )
        c.execute( users_t )
        c.execute( version_t )
        c.execute( version_r, (LOGDB_VERSION,))
        self.conn.commit()
        c.close()

    def log(self, user, message):
        log_query = '''INSERT INTO log(time, user, message)
                        VALUES (strftime('%Y-%m-%d %H:%M:%f','now'), ?, ? )'''
        c = self.conn.cursor()
        c.execute(log_query, (user, message))
        self.conn.commit()
        c.close()

    """
    Arguments are naively assumed to be of datetime type
    Comparing unixtimes just for the fucks of it
    Returning plain rows; output formatting is not of our concern
    """
    def fetch_last(self, start):
        """hi-pass filter"""
        fetch_query = '''SELECT time, user, message FROM log
                    WHERE strftime('%s', time) > ?'''
        start_ts = (start - BEGINNING_OF_TIMES).total_seconds()
        c = self.conn.cursor()
        c.execute(fetch_query, (start_ts,))
        raw_log = c.fetchall()
        c.close()
        return raw_log

    def fetch(self, start, end):
        """band-pass filter"""
        fetch_query = '''SELECT time, user, message FROM log
                    WHERE strftime('%s', time) > ?
                      AND strftime('%s', time) < ?'''
        start_ts = (start - BEGINNING_OF_TIMES).total_seconds()
        end_ts = (end - BEGINNING_OF_TIMES).total_seconds()
        c = self.conn.cursor()
        c.execute(fetch_query, (start_ts, end_ts))
        raw_log = c.fetchall()
        c.close()
        return raw_log

    def search(self, term):
        #stub
        return
