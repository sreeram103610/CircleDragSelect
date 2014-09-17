# Copyright 2013 Google Inc. All Rights Reserved.

"""Promotes Cloud SQL read replica to a stand-alone instance."""
from apiclient import errors

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import resources
from googlecloudsdk.sql import util


class PromoteReplica(base.Command):
  """Promotes Cloud SQL read replica to a stand-alone instance."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument('replica', help='Cloud SQL read replica ID.')

  def Run(self, args):
    """Promotes Cloud SQL read replica to a stand-alone instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the
      promote-replica operation if the promote-replica was successful.
    Raises:
      HttpException: An HTTP error response was received while executing api
          request.
      ToolException: An error other than an HTTP error occured while executing
          the command.
    """
    sql = self.context['sql']
    instance_id = util.GetInstanceIdWithoutProject(args.replica)
    project_id = util.GetProjectId(args.replica)
    # TODO(user): as we deprecate P:I args, simplify the call to .Parse().
    instance_ref = resources.Parse(
        instance_id, collection='sql.instances',
        params={'project': project_id})
    request = sql.instances().promoteReplica(project=instance_ref.project,
                                             instance=instance_ref.instance)
    try:
      result = request.execute()
      operations = self.command.ParentGroup().ParentGroup().operations()
      operation = operations.get(instance=str(instance_ref),
                                 operation=result['operation'])
      return operation
    except errors.HttpError as error:
      raise exceptions.HttpException(util.GetError(error))
    except errors.Error as error:
      raise exceptions.ToolException(error)

  # pylint: disable=unused-argument
  def Display(self, args, result):
    """Display information about what just happened to stdout.

    Args:
      args: The same as the args in Run.
      result: A dict object representing the operations resource describing the
          promote-replica operation if the promote-replica was successful.
    """
    printer = util.PrettyPrinter(0)
    printer.Print('Result of the promote-replica operation:')
    printer.PrintOperation(result)
