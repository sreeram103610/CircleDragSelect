# Copyright 2014 Google Inc. All Rights Reserved.

"""List printer for Cloud Platform resources."""

from googlecloudsdk.core.util import attrpath
from googlecloudsdk.core.util import console_io


def PrintResourceList(collection, items):
  """Print a list of cloud resources.

  Args:
    collection: str, The name of the collection to which the items belong.
    items: iterable, A list or otherwise iterable object that generates the
        rows of the list.
  """
  console_io.PrintExtendedList(items, COLLECTION_COLUMNS[collection])


def _Select(path, transform=None):
  """Get a column fetcher for the given attr path and transform.

  Args:
    path: str, The attr path that keys into the resource.
    transform: func(str)->str, A func that takes something found by the path
        and maps it to some other strip.

  Returns:
    func(obj)->str, A func that takes an object and returns the value
    for a particular column.
  """

  getter = attrpath.Selector(path)

  if transform is None:
    return getter
  def GetAndTransform(obj):
    return transform(getter(obj))
  return GetAndTransform


def _NameOnly(value):
  """Get only the last token from a longer path, usually the name.

  Intended to be a selector transform for URLs.

  Args:
    value: str, The value whose last token will be returned.

  Returns:
    str, The name from value.
  """
  if value:
    return value.split('/')[-1]
  return value


def _CommaList(default=None):
  def Transform(items):
    if not items:
      return default
    return ', '.join(items)
  return Transform



COLLECTION_COLUMNS = {
    # COMPUTE
    'compute.instances': (
        ('NAME', _Select('name')),
        ('ZONE', _Select('zone', _NameOnly)),
        ('MACHINE_TYPE', _Select('machineType', _NameOnly)),
        ('INTERNAL_IP', _Select('networkInterfaces[0].networkIP')),
        ('EXTERNAL_IP', _Select('networkInterfaces[0].accessConfigs[0].natIP')),
        ('STATUS', _Select('status')),
    ),

    # SQL
    'sql.backupRuns': (
        ('START', _Select('startTime')),
        ('END', _Select('endTime')),
        ('ERROR', _Select('error.code')),
        ('STATUS', _Select('status')),
    ),
    'sql.flags': (
        ('NAME', _Select('name')),
        ('TYPE', _Select('type')),
        ('ALLOWED_VALUES', _Select('allowedStringValues', _CommaList(''))),
    ),
    'sql.instances': (
        ('NAME', _Select('instance')),
        ('REGION', _Select('region')),
        ('TIER', _Select('settings.tier')),
        ('ADDRESS', _Select('ipAddresses[0].ipAddress')),
        ('STATUS', _Select('state')),
    ),
    'sql.operations': (
        ('OPERATION', _Select('operation')),
        ('TYPE', _Select('operationType')),
        ('START', _Select('startTime')),
        ('END', _Select('endTime')),
        ('ERROR', _Select('error')),
        ('STATUS', _Select('state')),
    ),
    'sql.sslCerts': (
        ('NAME', _Select('commonName')),
        ('SHA1_FINGERPRINT', _Select('sha1Fingerprint')),
        ('EXPIRATION', _Select('expirationTime')),
    ),
    'developerprojects.projects': (
        ('PROJECT', _Select('projectId')),
        ('TITLE', _Select('title')),
    )
}

