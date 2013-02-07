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


#Eneabegin
from sqlalchemy import Float
#Eneaend

from nova import log as logging


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine;
    # bind migrate_engine to your metadata
    meta = MetaData()
    meta.bind = migrate_engine
    compute_nodes = Table('compute_nodes', meta, autoload=True)

    #
    # New Columns
    #
    #Eneabegin
    new_columns = [
        Column('free_ram_mb', Integer()),
        Column('free_disk_gb', Integer()),
        Column('current_workload', Integer()),
        Column('running_vms', Integer()),
        Column('n_cpu_vms', Float()), #nummber of virtual machine classified CPU
        Column('n_io_vms', Float()),    #nummber of virtual machine classified IO
        Column('n_mem_vms', Float()),   #nummber of virtual machine classified MEM
        Column('n_und_vms', Float())   #nummber of virtual machine unclassified 
        ]
    #Eneaend
    for column in new_columns:
        compute_nodes.create_column(column)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    compute_nodes = Table('compute_nodes', meta, autoload=True)
    #Eneabegin
    for column in ('free_ram_mb',
                   'free_disk_gb',
                   'current_workload',
                   'running_vms',
                   'n_cpu_vms',  
                   'n_io_vms',
                   'n_mem_vms',
                   'n_und_vms'): 
        compute_nodes.drop_column(column)
    #Eneaend    