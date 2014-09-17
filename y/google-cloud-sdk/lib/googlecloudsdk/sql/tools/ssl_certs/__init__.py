# Copyright 2013 Google Inc. All Rights Reserved.

"""Provide commands for managing SSL certificates of Cloud SQL instances."""


from googlecloudsdk.calliope import base


class SslCerts(base.Group):
  """Provide commands for managing SSL certificates of Cloud SQL instances.

  Provide commands for managing SSL certificates of Cloud SQL instances,
  including creating, deleting, listing, and getting information about
  certificates.
  """

