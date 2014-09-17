# Copyright 2013 Google Inc. All Rights Reserved.

"""Provide commands for working with backups of Cloud SQL instances."""


from googlecloudsdk.calliope import base


class BackupRuns(base.Group):
  """Provide commands for working with backups of Cloud SQL instances.

  Provide commands for working with backups of Cloud SQL instances
  including listing and getting information about backups for a Cloud SQL
  instance.
  """

