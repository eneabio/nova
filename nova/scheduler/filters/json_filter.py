# Copyright (c) 2011 OpenStack, LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import json
import operator
from nova import utils

from nova import log as logging

from nova.scheduler import filters

LOG = logging.getLogger(__name__)

class JsonFilter(filters.BaseHostFilter):
    """Host Filter to allow simple JSON-based grammar for
    selecting hosts.
    """
    def _op_compare(self, args, op):
        """Returns True if the specified operator can successfully
        compare the first item in the args with all the rest. Will
        return False if only one item is in the list.
        """
        if len(args) < 2:
            return False
        if op is operator.contains:
            bad = not args[0] in args[1:]
        else:
            bad = [arg for arg in args[1:]
                    if not op(args[0], arg)]
        return not bool(bad)

    def _equals(self, args):
        """First term is == all the other terms."""
        return self._op_compare(args, operator.eq)

    def _less_than(self, args):
        """First term is < all the other terms."""
        return self._op_compare(args, operator.lt)

    def _greater_than(self, args):
        """First term is > all the other terms."""
        return self._op_compare(args, operator.gt)

    def _in(self, args):
        """First term is in set of remaining terms"""
        return self._op_compare(args, operator.contains)

    def _less_than_equal(self, args):
        """First term is <= all the other terms."""
        return self._op_compare(args, operator.le)

    def _greater_than_equal(self, args):
        """First term is >= all the other terms."""
        return self._op_compare(args, operator.ge)

    def _not(self, args):
        """Flip each of the arguments."""
        return [not arg for arg in args]

    def _or(self, args):
        """True if any arg is True."""
        return any(args)

    def _and(self, args):
        """True if all args are True."""
        return all(args)

    commands = {
        '=': _equals,
        '<': _less_than,
        '>': _greater_than,
        'in': _in,
        '<=': _less_than_equal,
        '>=': _greater_than_equal,
        'not': _not,
        'or': _or,
        'and': _and,
    }

    def _parse_string(self, string, host_state):
        """Strings prefixed with $ are capability lookups in the
        form '$variable' where 'variable' is an attribute in the
        HostState class.  If $variable is a dictionary, you may
        use: $variable.dictkey
        """
        #Eneabegin
        LOG.debug(_("Enea: in JsonFilter _parse_string") % locals())
        #Eneaend
        if not string:
            return None
        if not string.startswith("$"):
            return string

        path = string[1:].split(".")
        obj = getattr(host_state, path[0], None)
        if obj is None:
            return None
        for item in path[1:]:
            obj = obj.get(item, None)
            if obj is None:
                return None
        return obj

    def _process_filter(self, query, host_state):
        """Recursively parse the query structure."""
        #Eneabegin
        LOG.debug(_("Enea: in JsonFilter _process_filter") % locals())
        #Eneaend
        if not query:
            return True
        cmd = query[0]
        method = self.commands[cmd]
        cooked_args = []
        for arg in query[1:]:
            if isinstance(arg, list):   #Eneabegin if it is a list
                arg = self._process_filter(arg, host_state)
            elif isinstance(arg, basestring):    #Eneaend if it is a basestring
                arg = self._parse_string(arg, host_state)
            if arg is not None:
                cooked_args.append(arg)
        result = method(self, cooked_args)
        return result

    def host_passes(self, host_state, filter_properties):
        """Return a list of hosts that can fulfill the requirements
        specified in the query.
        """
        #Eneabegin
        LOG.debug(_("Enea: in JsonFilter _host_passes") % locals())
        #Verify if the host is up
        service = host_state.service
        if not utils.service_is_up(service) or service['disabled']:
            return False
        #Eneaend
        query = filter_properties.get('query', None)
        if not query:
            #Eneabegin
            LOG.debug(_("Enea: JsonFilter without query...host is passed automatically") % locals())
            #Eneaend
            return True

        # NOTE(comstud): Not checking capabilities or service for
        # enabled/disabled so that a provided json filter can decide

        result = self._process_filter(json.loads(query), host_state)
        if isinstance(result, list):
            # If any succeeded, include the host
            result = any(result)
        if result:
            # Filter it out.
            #Eneabegin
            LOG.debug(_("Enea: JsonFilter with query: %(query)s ...host is passed because it passes the query") % locals())
            #Eneaend
            return True
        return False
