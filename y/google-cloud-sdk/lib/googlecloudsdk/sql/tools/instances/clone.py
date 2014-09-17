# Copyright 2013 Google Inc. All Rights Reserved.

"""Clones a Cloud SQL instance."""
import json

from apiclient import errors

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import resources
from googlecloudsdk.sql import util


class Clone(base.Command):
  """Clones a Cloud SQL instance."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument(
        'source',
        help='Cloud SQL instance ID of the source.')
    parser.add_argument(
        'destination',
        help='Cloud SQL instance ID of the clone.')
    parser.add_argument(
        '--bin-log-file-name',
        required=False,
        help='Binary log file for the source instance.')
    parser.add_argument(
        '--bin-log-position',
        type=int,
        required=False,
        help='Position within the binary log file that represents the point'
        ' up to which the source is cloned.')

  def Run(self, args):
    """Clones a Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the
      clone operation if the clone was successful.
    Raises:
      InvalidArgumentException: If one of the simulateneously required arguments
          is not specified.
      HttpException: A http error response was received while executing api
          request.
      ToolException: An error other than http error occured while executing the
          command.
    """
    sql = self.context['sql']
    source_instance_name = util.GetInstanceIdWithoutProject(args.source)
    source_project_id = util.GetProjectId(args.source)
    # TODO(user): as we deprecate P:I args, simplify the call to .Parse().
    source_instance_ref = resources.Parse(
        source_instance_name, collection='sql.instances',
        params={'project': source_project_id})
    destination_instance_name = util.GetInstanceIdWithoutProject(
        args.destination)
    destination_project_id = util.GetProjectId(args.destination)
    # TODO(user): as we deprecate P:I args, simplify the call to .Parse().
    destination_instance_ref = resources.Parse(
        destination_instance_name, collection='sql.instances',
        params={'project': destination_project_id})
    if source_instance_ref.project != destination_instance_ref.project:
      raise exceptions.ToolException(
          'The source and the clone instance must belong to the same project:'
          ' "{src}" != "{dest}".' . format(
              src=source_instance_ref.project,
              dest=destination_instance_ref.project))

    clone_context = (
        '"kind": "sql#cloneContext", "sourceInstanceName": "%s"'
        ', "destinationInstanceName": "%s"' %
        (source_instance_ref.instance, destination_instance_ref.instance))

    bin_log_file_name = args.bin_log_file_name
    bin_log_position = args.bin_log_position

    if bin_log_file_name and bin_log_position:
      bin_log_coordinates = (
          '"kind": "sql#binLogCoordinates", "binLogFileName": "%s"'
          ', "binLogPosition": "%s"' % (bin_log_file_name, bin_log_position))
      clone_context += (', "binLogCoordinates": { %s }' % (bin_log_coordinates))
    elif  bin_log_file_name or bin_log_position:
      raise exceptions.ToolException(
          'Both --bin-log-file and --bin-log-file-name must be specified to'
          ' represent a valid binary log coordinate up to which the source is'
          ' cloned.')

    body = json.loads('{ "cloneContext" : { %s }}' % clone_context)
    request = sql.instances().clone(project=destination_instance_ref.project,
                                    body=body)
    try:
      result = request.execute()
      operations = self.command.ParentGroup().ParentGroup().operations()
      operation = operations.get(instance=str(destination_instance_ref),
                                 operation=result['operation'])
      return operation
    except errors.HttpError as error:
      raise exceptions.HttpException(util.GetError(error))
    except errors.Error as error:
      raise exceptions.ToolException(error)

  def Display(self, unused_args, result):
    """Display prints information about what just happened to stdout.

    Args:
      unused_args: The same as the args in Run.
      result: A dict object representing the operations resource describing the
      clone operation if the clone was successful.
    """
    printer = util.PrettyPrinter(0)
    printer.Print('Result of the clone operation:')
    printer.PrintOperation(result)
