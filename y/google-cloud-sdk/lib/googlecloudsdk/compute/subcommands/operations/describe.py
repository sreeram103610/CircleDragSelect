# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing operations."""
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.core import resources


class Describe(base_classes.BaseDescriber):
  """Describe a Google Compute Engine operation."""

  @staticmethod
  def Args(parser):
    base_classes.BaseDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'operations')

    scope = parser.add_mutually_exclusive_group()

    scope.add_argument(
        '--global',
        action='store_true',
        help=('If provided, it is assumed that the requested operation is '
              'global.'))

    scope.add_argument(
        '--region',
        help='The region of the operation to fetch.')

    scope.add_argument(
        '--zone',
        help='The zone of the operation to fetch.')

  @property
  def service(self):
    return self._service

  def CreateReference(self, args):
    try:
      ref = resources.Parse(args.name, params={
          'region': args.region, 'zone': args.zone})
    except resources.UnknownCollectionException:
      if getattr(args, 'global'):
        ref = self.CreateGlobalReference(
            args.name, resource_type='globalOperations')
      elif args.region:
        ref = self.CreateRegionalReference(
            args.name, args.region, resource_type='regionOperations')
      elif args.zone:
        ref = self.CreateZonalReference(
            args.name, args.zone, resource_type='zoneOperations')
      else:
        raise exceptions.ToolException(
            'Either pass in the full URI of an operation object or pass in '
            '[--global], [--region], or [--zone] when specifying just the '
            'operation name.')

    if ref.Collection() not in (
        'compute.globalOperations',
        'compute.regionOperations',
        'compute.zoneOperations'):
      raise exceptions.ToolException(
          'You must pass in a reference to a global, regional, or zonal '
          'operation.')
    else:
      if ref.Collection() == 'compute.globalOperations':
        self._service = self.context['compute'].globalOperations
      elif ref.Collection() == 'compute.regionOperations':
        self._service = self.context['compute'].regionOperations
      else:
        self._service = self.context['compute'].zoneOperations
      return ref

  def ScopeRequest(self, ref, request):
    if ref.Collection() == 'compute.regionOperations':
      request.region = ref.region
    elif ref.Collection() == 'compute.zoneOperations':
      request.zone = ref.zone


Describe.detailed_help = {
    'brief': 'Describe a Google Compute Engine operation',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Google Compute
        Engine operation in a project.
        """,
    'EXAMPLES': """\
        To get details about a global operation, run:

          $ {command} my-operation --global

        To get details about a regional operation, run:

          $ {command} my-operation --region us-central1

        To get details about a zonal operation, run:

          $ {command} my-operation --zone us-central1-a
        """,
}
