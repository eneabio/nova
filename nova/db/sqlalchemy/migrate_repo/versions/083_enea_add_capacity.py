# Copyright 2011 OpenStack LLC.
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

from sqlalchemy import Column, Integer, MetaData, Table

from nova import log as logging

#Eneabegin
from nova import flags
FLAGS = flags.FLAGS
#Eneaend

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine;
    # bind migrate_engine to your metadata
    meta = MetaData()
    meta.bind = migrate_engine
    compute_nodes = Table('compute_nodes', meta, autoload=True)
    
    #Eneabegin (from 4cde26d5 (Merge "Add a force_config_drive flag")
    #def _get_additional_capabilities():
    """Return additional capabilities to advertise for this compute host
    Kevin L. Mitchell    The brief description should end with a 'period', and there should be a É    Apr 27
    This will be replaced once HostAggrgates are able to handle more general
    host grouping for custom schedulers."""
    #capabilities = {}
    for cap in FLAGS.additional_compute_capabilities:
        if '=' in cap:
            name, value = cap.split('=', 1)
        else:
            name = cap
            value = True
        Column(name, Float())
        compute_nodes.create_column(Column) #new columns for capabilities
            #capabilities[name] = value
    #return capabilities
#Eneaend

def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    compute_nodes = Table('compute_nodes', meta, autoload=True)

    #Eneabegin
    for cap in FLAGS.additional_compute_capabilities:
        if '=' in cap:
            name, value = cap.split('=', 1)
        else:
            name = cap
            value = True
        Column(name, Float())
        compute_nodes.create_column(Column) #delete columns 
    #Eneaend