# Copyright 2013 Google Inc. All Rights Reserved.

"""Lists all SSL certs for a Cloud SQL instance."""
from apiclient import errors

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import resources
from googlecloudsdk.sql import util


class List(base.Command):
  """Lists all SSL certs for a Cloud SQL instance."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument(
        '--instance',
        '-i',
        required=True,
        help='Cloud SQL instance ID.')

  def Run(self, args):
    """Lists all SSL certs for a Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object that has the list of sslCerts resources if the api request
      was successful.
    Raises:
      HttpException: A http error response was received while executing api
          request.
      ToolException: An error other than http error occured while executing the
          command.
    """
    sql = self.context['sql']
    instance_id = util.GetInstanceIdWithoutProject(args.instance)
    project_id = util.GetProjectId(args.instance)
    # TODO(user): as we deprecate P:I args, simplify the call to .Parse().
    instance_ref = resources.Parse(
        instance_id, collection='sql.instances',
        params={'project': project_id})
    request = sql.sslCerts().list(project=instance_ref.project,
                                  instance=instance_ref.instance)
    try:
      result = request.execute()
      return result
    except errors.HttpError as error:
      raise exceptions.HttpException(util.GetError(error))
    except errors.Error as error:
      raise exceptions.ToolException(error)

  def Display(self, unused_args, result):
    """Display prints information about what just happened to stdout.

    Args:
      unused_args: The same as the args in Run.
      result: A dict object representing the operations resource if the api
      request was successful.
    """
    printer = util.PrettyPrinter(0)
    if result.has_key('items'):
      for cert in result['items']:
        printer.Print(cert['commonName'])
    else:
      printer.Print('No certs found for instances.')
