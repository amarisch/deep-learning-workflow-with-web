"""Streamline managing a single Azure resource group."""

from azure.mgmt.resource.resources import ResourceManagementClient


class ResourceHelper(object):
    """A helper class to manage details for a single resource group.
    Instantiate ResourceHelper with a name for the resource group
    through the resource_group_name kwarg. Thereafter, use the .group
    property to get the ResourceGroup object with the given name
    for the client_data credentials provided. If no such group
    exists, ResourceHelper will create one for you.
    """
    def __init__(self, client_data, location, group_name):
        self.location = location
        self.group_name = group_name
        self.resource_client = ResourceManagementClient(*client_data)
        self._resource_group = None

    @property
    def group(self):
        """Return this helper's ResourceGroup object.
        Look for the resource group for this object's client whose name
        matches default_name, and return it.
        If no such group exists, create it first.
        """
        if self._resource_group is None:
            print('Ensuring resource group...')
            resource_group = self.resource_client.resource_groups.create_or_update(
                self.group_name,
                {'location': self.location}
            )
            print('Got resource group:', resource_group.name)
            self._resource_group = resource_group
        return self._resource_group

    def list_resources(self):
        """List resources in this helper's resource group."""
        return self.resource_client.resource_groups.list_by_resource_group(self.group_name)

    def get_by_id(self, resource_id):
        """Get a resource by id from this helper's resource group."""
        return self.resource_client.resources.get_by_id(resource_id, '2017-04-01')

    def delete_group(self):
        self.resource_client.resource_groups.delete(self.group_name)

    def print_group_info(self):
        """Print a ResourceGroup instance."""
        print("\tName: {}".format(self.group.name))
        print("\tId: {}".format(self.group.id))
        print("\tLocation: {}".format(self.group.location))
        print("\tTags: {}".format(self.group.tags))