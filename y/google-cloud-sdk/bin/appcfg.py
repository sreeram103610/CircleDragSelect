#!/usr/bin/env python
#
# Copyright 2013 Google Inc. All Rights Reserved.
#

"""A convenience wrapper for starting appengine for python."""

import bootstrapping.bootstrapping as bootstrapping

from googlecloudsdk.core import config


def main():
  """Launches appcfg.py."""

  unused_project, account = bootstrapping.GetActiveProjectAndAccount()
  json_creds = config.Paths().LegacyCredentialsJSONPath(account)

  args = [
      '--oauth2',
      '--oauth2_client_id=32555940559.apps.googleusercontent.com',
      '--oauth2_client_secret=ZmssLNjJy2998hD4CTg2ejr2',
      '--oauth2_credential_file={0}'.format(json_creds),
      '--skip_sdk_update_check'
  ]

  bootstrapping.ExecutePythonTool('platform/google_appengine', 'appcfg.py', *args)


if __name__ == '__main__':
  bootstrapping.CommandStart('appcfg', component_id='gae-python')
  bootstrapping.PrerunChecks()
  main()
