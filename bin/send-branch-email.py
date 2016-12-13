#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is a script to send global site notification emails.

It should only be used for important transactional messages like a Terms of
Service change. Process:

    - write your email in emails/branch.spt
    - test locally using your own database and AWS keys in local.env
    - when reviewed and merged:
        - deploy
        - `heroku run bash`
        - `bin/send-branch-email.py username`           # final test from production
        - `bin/send-branch-email.py all 2> queued.log`  # !!!
        - make a commit to master to remove branch.spt
        - push to GitHub

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import random
import sys

from gratipay.main import website


def prompt(msg):
    answer = raw_input(msg + " [y/N]")
    if answer.lower() != 'y':
        raise SystemExit(1)


# Fetch participants.
# ===================

try:
    username = sys.argv[1]
except KeyError:
    print("Usage: {} {username|all}".format(sys.argv[0]))

if username == 'all':
    prompt("Are you ready?")
    prompt("Are you REALLY ready?")
    prompt("... ?")
    print("Okay, you asked for it!")
    participants = website.db.all("""
        SELECT p.*::participants
          FROM participants p
         WHERE email_address is not null
           AND claimed_time  is not null
           AND is_closed     is not true
           AND is_suspicious is not true
    """)
else:
    participants = website.db.all("SELECT p.*::participants FROM participants p "
                                  "WHERE p.username=%s", username)

N = len(participants)
print(N)
print([(p.username, p.email_address) for p in random.sample(participants, 5 if N > 5 else 1)])


# Send emails.
# ============

if username == 'all':
    prompt("But really actually tho? I mean, ... seriously?")

for p in participants:
    print("Queuing for {} ({}={}).".format(p.email_address, p.username, p.id), file=sys.stderr)
    p.queue_email('branch', include_unsubscribe=False)
