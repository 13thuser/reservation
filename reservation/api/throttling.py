from django.core.cache import caches
from django.core.exceptions import ImproperlyConfigured

from rest_framework.throttling import ScopedRateThrottle


class ResourceBasedScopedRateThrottle(ScopedRateThrottle):
    cache = caches['api']

    def __init__(self, resource_id, get_method_group_id=lambda x: x):
        self.resource_id = resource_id
        self.get_method_group_id = get_method_group_id
        super(ResourceBasedScopedRateThrottle, self).__init__()

    def get_cache_key(self, request, view):
        method = self.get_method_group_id(request.method.lower())
        view_name = view.get_view_name().lower().replace(' ', '_')
        scope = '{}_{}_{}_{}'.format(
            self.scope, view_name, method, self.resource_id)

        return self.cache_format % {
            'scope': scope,
            'ident': 'all'
        }


class MethodBasedThrottlingMixin(object):
    # Choose what throttling policy you want to choose
    # NOTE: Mutually exclusive
    # Choose what methods to unthrottle
    UNTHROTTLED_METHODS = set()
    # Choose what methods to throttle
    THROTTLED_METHODS = set()
    resource_id_field = 'pk'

    def __init__(self, *args, **kwargs):
        if (self.UNTHROTTLED_METHODS and self.THROTTLED_METHODS):
            raise ImproperlyConfigured('UNTHROTTLED_METHODS and '
                                       'THROTTLED_METHODS are mutually '
                                       'exclusive options.')

    def get_method_group_id(self, method):
        return method

    def get_throttles(self):
        resource_id = self.kwargs.get(self.resource_id_field)
        method = self.request.method.lower()
        if (self.UNTHROTTLED_METHODS and
                method in self.UNTHROTTLED_METHODS):
            return []
        if (not self.THROTTLED_METHODS or
                method in self.THROTTLED_METHODS):
            return [ResourceBasedScopedRateThrottle(resource_id,
                                                    self.get_method_group_id)]
        return []
