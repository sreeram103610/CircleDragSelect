# Copyright 2013 Google Inc. All Rights Reserved.

"""Retrieves information about an SSL cert for a Cloud SQL instance."""
from apiclient import errors

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import resources
from googlecloudsdk.sql import util


class Get(base.Command):
  """Retrieves information about an SSL cert for a Cloud SQL instance."""

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
    """Retrieves information about an SSL cert for a Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the sslCerts resource if the api request was
      successful.
    Raises:
      HttpException: A http error response was received while executing api
          request.
      ToolException: An error other than http error occured while executing the
          command.
    """
    common_name = args.common_name
    instance_id = util.GetInstanceIdWithoutProject(args.instance)
    project_id = util.GetProjectId(args.instance)
    # TODO(user): as we deprecate P:I args, simplify the call to .Parse().
    instance_ref = resources.Parse(
        instance_id, collection='sql.instances',
        params={'project': project_id})
    try:
      ssl_certs = self.command.ParentGroup().list(
          instance=instance_ref.instance)
      for cert in ssl_certs['items']:
        # TODO(user): figure out how to rectify the common_name and the
        # sha1fingerprint, so that things can work with the resource parser.
        if cert.get('commonName') == common_name:
          return cert
      raise exceptions.ToolException('Cert with the provided common name '
                                     'doesn\'t exist.')
    except errors.HttpError as error:
      raise exceptions.HttpException(util.GetError(error))
    except errors.Error as error:
      raise exceptions.ToolException(error)

  def Display(self, unused_args, result):
    """Display prints information about what just happened to stdout.

    Args:
      unused_args: The same as the args in Run.
      result: A dict object representing the sslCert resource if the api
      request was successful.
    """
    printer = util.PrettyPrinter(0)
    printer.PrintSslCert(result)
