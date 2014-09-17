# Copyright 2013 Google Inc. All Rights Reserved.

"""Deletes an SSL certificate for a Cloud SQL instance."""
from apiclient import errors

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import resources
from googlecloudsdk.sql import util


class Delete(base.Command):
  """Deletes an SSL certificate for a Cloud SQL instance."""

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
    parser.add_argument(
        'common_name',
        help='User supplied name. Constrained to [a-zA-Z.-_ ]+.')

  def Run(self, args):
    """Deletes an SSL certificate for a Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the delete
      operation if the api request was successful.
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
    # TODO(user): figure out how to rectify the common_name and the
    # sha1fingerprint, so that things can work with the resource parser.
    common_name = args.common_name
    try:
      ssl_certs = self.command.ParentGroup().list(instance=str(instance_ref))
      for cert in ssl_certs['items']:
        if cert.get('commonName') == common_name:
          sha1_fingerprint = cert.get('sha1Fingerprint')
          request = sql.sslCerts().delete(project=instance_ref.project,
                                          instance=instance_ref.instance,
                                          sha1Fingerprint=sha1_fingerprint)
          result = request.execute()
          operations = self.command.ParentGroup().ParentGroup().operations()
          operation = operations.get(instance=str(instance_ref),
                                     operation=result['operation'])
          return operation
      raise exceptions.ToolException('Cert with the provided common name '
                                     'doesn\'t exist.')
    except errors.HttpError as error:
      raise exceptions.HttpException(util.GetError(error))

  # pylint: disable=unused-argument
  def Display(self, args, result):
    """Display prints information about what just happened to stdout.

    Args:
      args: The same as the args in Run.
      result: A dict object representing the operations resource describing the
          delete operation if the delete was successful.
    """
    printer = util.PrettyPrinter(0)
    printer.Print('Result of the delete operation:')
    printer.PrintOperation(result)

