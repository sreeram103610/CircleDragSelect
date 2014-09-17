#!/usr/bin/env python
#
# Copyright 2013 Google Inc. All Rights Reserved.
#

"""A convenience wrapper for starting endpoints for appengine for python."""

import bootstrapping.bootstrapping as bootstrapping


def main():
  """Launches dev_appserver.py."""

  bootstrapping.ExecutePythonTool(
      'platform/google_appengine', 'endpointscfg.py')


if __name__ == '__main__':
  bootstrapping.CommandStart('endpointscfg', component_id='gae-python')
  bootstrapping.CheckUpdates()
  main()
