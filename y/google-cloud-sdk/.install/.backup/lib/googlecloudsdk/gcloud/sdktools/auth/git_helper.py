# Copyright 2013 Google Inc. All Rights Reserved.

"""A git credential helper that provides Google git repository passwords.

Reads a session from stdin that looks a lot like:
  protocol=https
  host=code.google.com
And writes out a session to stdout that looks a lot like:
  username=me
  password=secret

When the provided host is wrong, no username or password will be provided.
"""
import os
import re
import sys
import textwrap

import httplib2
from oauth2client import client

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exc
from googlecloudsdk.core import properties
from googlecloudsdk.core.credentials import store as c_store


_KEYVAL_RE = re.compile(r'(.+)=(.+)')


@base.Hidden
class GitHelper(base.Command):
  """A git credential helper to provide access to Google git repositories."""

  @staticmethod
  def Args(parser):
    parser.add_argument('method',
                        help='The git credential helper method.')

  @c_exc.RaiseToolExceptionInsteadOf(c_store.Error, client.Error)
  def Run(self, args):
    """Run the helper command."""

    if args.method != 'get':
      return

    info = {}

    lines = sys.stdin.readlines()
    for line in lines:
      match = _KEYVAL_RE.match(line)
      if not match:
        continue
      key, val = match.groups()
      info[key] = val.strip()

    if info.get('protocol') != 'https':
      return

    credentialed_domains = ['code.google.com', 'source.developers.google.com']
    extra = properties.VALUES.core.credentialed_hosted_repo_domains.Get()
    if extra:
      credentialed_domains.extend(extra.split(','))
    if info.get('host') not in credentialed_domains:
      return

    account = properties.VALUES.core.account.Get()

    try:
      cred = c_store.Load(account)
    except c_store.Error as e:
      sys.stderr.write(textwrap.dedent("""\
          ERROR: {error}
          Run 'gcloud auth login' to log in.
          """.format(error=str(e))))
      return

    cred.refresh(httplib2.Http())

    self._CheckNetrc()

    sys.stdout.write(textwrap.dedent("""\
        username={username}
        password={password}
        """).format(username=account, password=cred.access_token))

  def _CheckNetrc(self):
    def Check(p):
      if not os.path.exists(p):
        return
      try:
        with open(p) as f:
          data = f.read()
          if ('code.google.com' in data or
              'source.developers.google.com' in data):
            sys.stderr.write(textwrap.dedent("""\
You have credentials for your Google repository in [{path}]. This repository's
git credential helper is set correctly, so the credentials in [{path}] will not
be used, but you may want to remove them to avoid confusion.
""".format(path=p)))
      # pylint:disable=broad-except, If something went wrong, forget about it.
      except Exception:
        pass
    Check(os.path.expanduser(os.path.join('~', '.netrc')))
    Check(os.path.expanduser(os.path.join('~', '_netrc')))
