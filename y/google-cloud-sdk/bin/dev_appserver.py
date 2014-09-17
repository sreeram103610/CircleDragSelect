#!/usr/bin/env python
#
# Copyright 2013 Google Inc. All Rights Reserved.
#

"""A convenience wrapper for starting dev_appserver for appengine for python."""

import os

import bootstrapping.bootstrapping as bootstrapping

from googlecloudsdk.core.util import platforms


def main():
  """Launches dev_appserver.py."""

  args = [
      '--skip_sdk_update_check=True'
  ]
  if platforms.OperatingSystem.Current() == platforms.OperatingSystem.MACOSX:
    php_path = os.path.join(bootstrapping.BOOTSTRAPPING_DIR, 'php-cgi')
    if os.path.exists(php_path):
      args.append('--php_executable_path=' + php_path)
  # The executable for Windows will be in the correct default location.

  bootstrapping.ExecutePythonTool(
      'platform/google_appengine', 'dev_appserver.py', *args)


if __name__ == '__main__':
  bootstrapping.CommandStart('dev_appserver', component_id='gae-python')
  bootstrapping.CheckUpdates()
  main()
