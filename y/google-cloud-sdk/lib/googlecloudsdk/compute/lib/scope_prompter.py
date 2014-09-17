# Copyright 2014 Google Inc. All Rights Reserved.
"""Facilities for user prompting for request context."""

import abc

from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import lister
from googlecloudsdk.compute.lib import utils
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources
from googlecloudsdk.core.util import console_io


class ScopePrompter(object):
  """A mixin class prompting in the case of ambiguous resource context."""

  __metaclass__ = abc.ABCMeta

  def GetCollection(self, resource_type):
    """Coverts a resource type to a collection."""
    if resource_type == 'zoneViews':
      return 'resourceviews.{0}'.format(resource_type)
    else:
      return 'compute.{0}'.format(resource_type or self.resource_type)

  def HasDefaultValue(self, resource_type, scope_name):
    """Returns whether the scope has a default value."""
    collection = self.GetCollection(resource_type)
    api = utils.CollectionToApi(collection)
    try:
      resources.GetParamDefault(
          api=api,
          collection=resource_type,
          param=scope_name)
      return True
    except properties.RequiredPropertyError:
      return False

  def FetchChoices(self, attribute, service, flag_name, prefix_filter=None):
    """Returns a list of choices used to prompt with."""
    if prefix_filter:
      filter_expr = 'name eq {0}.*'.format(prefix_filter)
    else:
      filter_expr = None

    errors = []
    global_resources = lister.GetGlobalResources(
        service=service,
        project=self.context['project'],
        filter_expr=filter_expr,
        http=self.context['http'],
        batch_url=self.context['batch-url'],
        errors=errors)

    choices = [resource.name for resource in global_resources]
    if errors or not choices:
      punctuation = ':' if errors else '.'
      utils.RaiseToolException(
          errors,
          'Unable to fetch a list of {0}s. Specifying [{1}] may fix this '
          'issue{2}'.format(attribute, flag_name, punctuation))

    return choices

  def PromptForScope(self, ambiguous_refs, attribute, service, resource_type,
                     flag_name, prefix_filter):
    """Prompts the user to resolve abiguous resources."""
    # targetInstances -> target instances
    resource_name = utils.CamelCaseToOutputFriendly(resource_type)
    # Resource names should be surrounded by brackets while choices should not
    names = ['[{0}]'.format(name) for name, _ in ambiguous_refs]
    choices = self.FetchChoices(attribute, service, flag_name, prefix_filter)
    title = utils.ConstructList(
        'For the following {0}:'.format(resource_name), names)
    idx = console_io.PromptChoice(
        options=choices,
        message='{0}choose a {1}:'.format(title, attribute))
    if idx is None:
      raise exceptions.ToolException(
          'Unable to prompt. Specify the [{0}] flag.'.format(flag_name))
    choice = choices[idx]
    for _, resource_ref in ambiguous_refs:
      setattr(resource_ref, attribute, choice)

  def CreateScopedReferences(self, resource_names, scope_name, scope_arg,
                             scope_service, resource_type, flag_name,
                             prefix_filter=None):
    """Returns a list of resolved resource references for scoped resources."""
    resource_refs = []
    ambiguous_refs = []
    for resource_name in resource_names:
      resource_ref = resources.Parse(
          resource_name,
          collection=self.GetCollection(resource_type),
          params={scope_name: scope_arg},
          resolve=False)
      resource_refs.append(resource_ref)
      if not getattr(resource_ref, scope_name):
        ambiguous_refs.append((resource_name, resource_ref))

    has_default = self.HasDefaultValue(resource_type, scope_name)
    if ambiguous_refs and not scope_arg and not has_default:
      # We need to prompt.
      self.PromptForScope(
          ambiguous_refs=ambiguous_refs,
          attribute=scope_name,
          service=scope_service,
          resource_type=resource_type or self.resource_type,
          flag_name=flag_name,
          prefix_filter=prefix_filter)

    for resource_ref in resource_refs:
      resource_ref.Resolve()

    return resource_refs

  def CreateZonalReferences(self, resource_names, zone_arg, resource_type=None,
                            flag_name='--zone', region_filter=None):
    """Returns a list of resolved zonal resource references."""
    if zone_arg:
      zone_ref = resources.Parse(zone_arg, collection='compute.zones')
      zone_name = zone_ref.Name()
    else:
      zone_name = None

    return self.CreateScopedReferences(
        resource_names,
        scope_name='zone',
        scope_arg=zone_name,
        scope_service=self.context['compute'].zones,
        resource_type=resource_type,
        flag_name=flag_name,
        prefix_filter=region_filter)

  def CreateZonalReference(self, resource_name, zone_arg, resource_type=None,
                           flag_name='--zone', region_filter=None):
    return self.CreateZonalReferences(
        [resource_name], zone_arg, resource_type, flag_name, region_filter)[0]

  def CreateRegionalReferences(self, resource_names, region_arg,
                               flag_name='--region', resource_type=None):
    """Returns a list of resolved regional resource references."""
    if region_arg:
      region_ref = resources.Parse(region_arg, collection='compute.regions')
      region_name = region_ref.Name()
    else:
      region_name = None

    return self.CreateScopedReferences(
        resource_names,
        scope_name='region',
        scope_arg=region_name,
        scope_service=self.context['compute'].regions,
        flag_name=flag_name,
        resource_type=resource_type)

  def CreateRegionalReference(self, resource_name, region_arg,
                              flag_name='--region', resource_type=None):
    return self.CreateRegionalReferences(
        [resource_name], region_arg, flag_name, resource_type)[0]

  def CreateGlobalReferences(self, resource_names, resource_type=None):
    """Returns a list of resolved global resource references."""
    resource_refs = []
    for resource_name in resource_names:
      resource_refs.append(resources.Parse(
          resource_name,
          collection=self.GetCollection(resource_type)))
    return resource_refs

  def CreateGlobalReference(self, resource_name, resource_type=None):
    return self.CreateGlobalReferences([resource_name], resource_type)[0]
