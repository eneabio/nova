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
"""
Least Cost is an algorithm for choosing which host machines to
provision a set of resources to. The input is a WeightedHost object which
is decided upon by a set of objective-functions, called the 'cost-functions'.
The WeightedHost contains a combined weight for each cost-function.

The cost-function and weights are tabulated, and the host with the least cost
is then selected for provisioning.
"""

from nova import flags
from nova import log as logging
from nova.openstack.common import cfg
import base64
from nova.db import api as apidb
from nova.scheduler import api
from nova.scheduler import host_manager
from nova.compute import manager
from nova.compute import api as apicompute
from nova import rpc


LOG = logging.getLogger(__name__)

least_cost_opts = [
    cfg.ListOpt('least_cost_functions',
                default=[
                  'nova.scheduler.least_cost.compute_fill_first_cost_fn'
                  ],
                help='Which cost functions the LeastCostScheduler should use'),
    cfg.FloatOpt('noop_cost_fn_weight',
             default=1.0,
               help='How much weight to give the noop cost function'),
    cfg.FloatOpt('compute_fill_first_cost_fn_weight',
             default=-1.0,
               help='How much weight to give the fill-first cost function. '
                    'A negative value will reverse behavior: '
                    'e.g. spread-first'),
    ]

FLAGS = flags.FLAGS
FLAGS.register_opts(least_cost_opts)

# TODO(sirp): Once we have enough of these rules, we can break them out into a
# cost_functions.py file (perhaps in a least_cost_scheduler directory)


class WeightedHost(object):
    """Reduced set of information about a host that has been weighed.
    This is an attempt to remove some of the ad-hoc dict structures
    previously used."""

    def __init__(self, weight, host_state=None):
        self.weight = weight
        self.host_state = host_state

    def to_dict(self):
        x = dict(weight=self.weight)
        if self.host_state:
            x['host'] = self.host_state.host
        return x


def noop_cost_fn(host_state, weighing_properties):
    """Return a pre-weight cost of 1 for each host"""
    return 1

#Eneabegin
def compute_fill_first_cost_fn(host_state, weighing_properties):
    """More free ram = higher weight. So servers will less free
    ram will be preferred."""
    return host_state.free_ram_mb

def compute_fill_first_cost_Enea_fn(host_state, weighing_properties):
    #Ricordarsi di cambiare il flag in Nova per usare questa funzione al posto di quella originale
    #Eneabegin
    """Select host with ...."""
    #Proprieta' dell'istanza richiesta, user_data indica la classe dell'istanza...
    user_data_encode = weighing_properties['request_spec']['instance_properties']['user_data']
    user_data=base64.b64decode(user_data_encode)
    pesoA=1000;
    pesoB=-1;
    pesoC=1;
    cost=0;
    #host_state.capabilities
    #capabilities is a dictionary?
    #BetaCpuHost = host_state.capabilities
    #capabilities = host_manager.HostManager.get_all_host_states(weighing_properties['context'], 'compute')
    context=weighing_properties['context']
    remote_address = context.remote_address
    #capabilities=apicompute._cast_or_call_compute_message(rpc.call, '_get_additional_capabilities', context, host) 

    #prende sempre lo stesso host
    #capabilities=manager._get_additional_capabilities()
    host=host_state.host
    service_schedulers = apidb.service_get_all_by_topic(context, 'scheduler')
    #choice the correct scheduler, it could be with the zone, now it choices the first
    scheduler_host= service_schedulers[0]['host']
    service='scheduler.'
    service=service+scheduler_host
    LOG.debug(_('Enea: scheduler host in scheduler-least_cost is %s') % service)
    #da togliere rpc.call, blocca lo scheduler in attesa della risposta
    #preferibile usare host_state del corretto host guardando i dizionari
    caps = rpc.call(context, service, {"method": "get_service_capabilities","arg":{"host":host_state.host}})
    #ricordarsi di cambiare essex1 con il nome variabile dell'host
    #caps = rpc.call(context, 'scheduler.essex1', {"method": "get_service_capabilities","arg":{"host":host_state.host}})
    #caps['compute_beta_cpu'][0]
    LOG.debug(_('Enea: host_name in scheduler-least_cost is %s') % host_state.host)
    LOG.debug(_('Enea: beta_cpu in scheduler-least_cost is %s') % caps[host]['compute']['beta_cpu'])
    #BetaCpuHost = float(capabilities['beta_cpu'])
    #BetaIoHost = float(capabilities['beta_io'])
    #BetaMemHost = float(capabilities['beta_mem']) 
    #BetaUndHost = float(capabilities['beta_und'])
    #capabilities=api.get_service_capabilities(context)
    BetaCpuHost = float(caps[host]['compute']['beta_cpu'])
    BetaIoHost = float(caps[host]['compute']['beta_io'])
    BetaMemHost = float(caps[host]['compute']['beta_mem'])
    BetaUndHost = float(caps[host]['compute']['beta_und'])
    #LOG.debug(_('Enea: capabilities: %s') % capabilities)
    #LOG.debug(_('Enea: Host_state in scheduler-least_cost is %(host_state)s') % locals())
    #LOG.debug(_('Enea: weighing_properties in scheduler-least_cost for host %(host_state.host)s is %(weighing_properties)s') % locals())
    #LOG.debug(_('Enea: host_state_capabilities %(capabilities)s in '
    #                    '%(host_name)s'),
    #                    {'host_state_capabilities': capabilities,
    #                    'host_name': host_state.host})
    #Calcolo beta cappuccio, devo trovare il modo di passare la classe di istanza richiesta...
    running_vms = host_state.n_cpu_vms + host_state.n_io_vms + host_state.n_mem_vms + host_state.n_und_vms
    #LOG.debug(_('Enea: Running_vms in scheduler-least_cost is %(running_vms)s') % locals())
    #LOG.debug(_('Enea: n_cpu_vms in scheduler-least_cost is %s') % host_state.n_cpu_vms/2)
    #LOG.debug(_('Enea: Running_vms in scheduler-least_cost is %s') % running_vms/2)
    if user_data == 'cpu':
        if running_vms==0:
                newBetaCpu = (host_state.n_cpu_vms+1)/(running_vms+1)
                cost=(host_state.n_cpu_vms)*pesoA+pesoB*(running_vms)+pesoC*(newBetaCpu-BetaCpuHost)
        else:
                newBetaCpu = ((host_state.n_cpu_vms/2)+1)/((running_vms/2)+1)
                cost=(host_state.n_cpu_vms/2)*pesoA+pesoB*(running_vms/2)+pesoC*(newBetaCpu-BetaCpuHost)
    if user_data == 'io':
        if running_vms==0:
                newBetaIo = (host_state.n_io_vms+1)/(running_vms+1)
                cost=(host_state.n_io_vms)*pesoA+pesoB*(running_vms)+pesoC*(newBetaIo-BetaIoHost)
        else:
                newBetaIo = ((host_state.n_io_vms/2)+1)/((running_vms/2)+1)
                cost=(host_state.n_io_vms/2)*pesoA+pesoB*(running_vms/2)+pesoC*(newBetaIo-BetaIoHost)
    if user_data == 'mem':
        if running_vms==0:
                newBetaMem = (host_state.n_mem_vms+1)/(running_vms+1)
                cost=(host_state.n_mem_vms)*pesoA+pesoB*(running_vms)+pesoC*(newBetaMem-BetaMemHost)
        else:
                newBetaMem = ((host_state.n_mem_vms/2)+1)/((running_vms/2)+1)
                cost=(host_state.n_mem_vms/2)*pesoA+pesoB*(running_vms/2)+pesoC*(newBetaMem-BetaMemHost)
    if user_data == 'und':
        if running_vms==0:
                newBetaUnd = (host_state.n_und_vms+1)/(running_vms+1)
                cost=(host_state.n_und_vms)*pesoA+pesoB*(running_vms)+pesoC*(newBetaUnd-BetaUndHost)
        else:
                newBetaUnd = ((host_state.n_und_vms/2)+1)/((running_vms/2)+1)
                cost=(host_state.n_und_vms/2)*pesoA+pesoB*(running_vms/2)+pesoC*(newBetaUnd-BetaUndHost)

    LOG.debug(_('Enea: Cost in scheduler least_cost is %(cost)s') % locals())
    return cost
#Eneaend



def weighted_sum(weighted_fns, host_states, weighing_properties):
    """Use the weighted-sum method to compute a score for an array of objects.

    Normalize the results of the objective-functions so that the weights are
    meaningful regardless of objective-function's range.

    :param host_list:    ``[(host, HostInfo()), ...]``
    :param weighted_fns: list of weights and functions like::

        [(weight, objective-functions), ...]

    :param weighing_properties: an arbitrary dict of values that can
        influence weights.

    :returns: a single WeightedHost object which represents the best
              candidate.
    """

    # Make a grid of functions results.
    # One row per host. One column per function.
    scores = []
    for weight, fn in weighted_fns:
        scores.append([fn(host_state, weighing_properties)  #Enea: calcola tutte le funzioni fn
                for host_state in host_states])

    # Adjust the weights in the grid by the functions weight adjustment
    # and sum them up to get a final list of weights.
    adjusted_scores = []
    for (weight, fn), row in zip(weighted_fns, scores):
        adjusted_scores.append([weight * score for score in row])

    # Now, sum down the columns to get the final score. Column per host.
    final_scores = [0.0] * len(host_states)
    for row in adjusted_scores:
        for idx, col in enumerate(row):
            final_scores[idx] += col

    # Super-impose the host_state into the scores so
    # we don't lose it when we sort.
    final_scores = [(final_scores[idx], host_state)
            for idx, host_state in enumerate(host_states)]

    final_scores = sorted(final_scores)
    weight, host_state = final_scores[0]  # Lowest score is the winner!
    return WeightedHost(weight, host_state=host_state)
