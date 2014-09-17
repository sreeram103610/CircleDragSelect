# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for adding instances to target pools."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import utils


class AddInstances(base_classes.NoOutputAsyncMutator):
  """Add instances to a target pool."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--instances',
        help='Specifies a list of instances to add to the target pool.',
        metavar='INSTANCE',
        nargs='+',
        required=True)

    utils.AddZoneFlag(
        parser,
        resource_type='instances',
        operation_type='add to the target pool')

    parser.add_argument(
        'name',
        help='The name of the target pool to which to add the instances.')

  @property
  def service(self):
    return self.context['compute'].targetPools

  @property
  def method(self):
    return 'AddInstance'

  @property
  def resource_type(self):
    return 'targetPools'

  def CreateRequests(self, args):
    instance_refs = self.CreateZonalReferences(
        args.instances, args.zone, resource_type='instances')

    instances = [messages.InstanceReference(instance=instance_ref.SelfLink())
                 for instance_ref in instance_refs]

    unique_regions = set(utils.ZoneNameToRegionName(instance_ref.zone)
                         for instance_ref in instance_refs)

    # Check that all regions are the same.
    if len(unique_regions) > 1:
      raise calliope_exceptions.ToolException(
          'Instances must all be in the same region as the target pool.')

    target_pool_ref = self.CreateRegionalReference(
        args.name, unique_regions.pop(),
        resource_type='targetPools')

    request = messages.ComputeTargetPoolsAddInstanceRequest(
        region=target_pool_ref.region,
        project=self.context['project'],
        targetPool=target_pool_ref.Name(),
        targetPoolsAddInstanceRequest=messages.TargetPoolsAddInstanceRequest(
            instances=instances))
    return [request]


AddInstances.detailed_help = {
    'brief': 'Add instances to a target pool',
    'DESCRIPTION': """\
        *{command}* is used to add one or more instances to a target pool.
        For more information on health checks and load balancing, see
        link:https://developers.google.com/compute/docs/load-balancing/[].
        """,
}
