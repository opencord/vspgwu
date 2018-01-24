# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
from django.db.models import Q, F
from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible

from collections import defaultdict

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

class ServiceGraphException(Exception):
    pass

class SyncVSPGWUTenant(SyncInstanceUsingAnsible):
    observes = VSPGWUTenant
    template_name = "vspgwutenant_playbook.yaml"
    service_key_name = "/opt/xos/configurations/mcord/mcord_private_key"

    """ Convert ServiceInstance graph into an adjacency set"""
    def adj_set_of_service_graph(self, o, visited = None, adj_set = None):
        def key(o):
            return o.leaf_model_name

        if not adj_set:
            adj_set = defaultdict(set)

        if not o:
            return adj_set
        else:
            if not visited:
                visited = set()

            ko = key(o)
            visited.add(ko)

            provider_links = ServiceInstanceLink.objects.filter(subscriber_service_instance_id = o.id)
            for l in provider_links:
                n = l.provider_service_instance
                kn = key(n)
                adj_set[ko].add(kn)
                adj_set[kn].update([])
                if kn not in visited:
                    adj_set = self.adj_set_of_service_graph(n, visited, adj_set)

            subscriber_links = ServiceInstanceLink.objects.filter(provider_service_instance_id = o.id)
            for l in subscriber_links:
                n = l.subscriber_service_instance
                sn = key(n)
                adj_set[sn].add(ko)
                adj_set[ko].update([])
                if sn not in visited:
                    adj_set = self.adj_set_of_service_graph(n, visited, adj_set)

            return adj_set

    def __init__(self, *args, **kwargs):
        super(SyncVSPGWUTenant, self).__init__(*args, **kwargs)

    def get_extra_attributes(self, o):
        blueprint = self.get_blueprint_and_check_dependencies(o)

        if blueprint == 'cord_4_1_blueprint':
            return self.get_values_for_CORD_4_1(o)
        elif blueprint == 'cord_5_0_blueprint':
            return self.get_values_for_CORD_5_0(o)
        else:
            return self.get_extra_attributes_for_manual(o)

    # fields for manual case
    def get_extra_attributes_for_manual(self, o):
        fields = {}
        fields['blueprint'] = "manual"
        fields['cord_version'] = "manual"
        # for interface.cfg file
        fields['zmq_sub_ip'] = "manual"
        fields['zmq_pub_ip'] = "manual"
        fields['dp_comm_ip'] = "manual"
        fields['cp_comm_ip'] = "manual"
        fields['fpc_ip'] = "manual"
        fields['cp_nb_server_ip'] = "manual"

        # for dp_config.cfg file
        fields['s1u_ip'] = "manual"
        fields['sgi_ip'] = "manual"

        # for static_arp.cfg file
        fields['as_sgi_ip'] = "manual"
        fields['as_sgi_mac'] = "manual"
        fields['enb_s1u_ip'] = "manual"
        fields['enb_s1u_mac'] = "manual"

        return fields

    def get_values_for_CORD_4_1(self, o):
        fields = {}
        fields['cord_version'] = "4.1"
        fields['blueprint'] = "cord_4_1_blueprint"
        # for interface.cfg file
        fields['zmq_sub_ip'] = "127.0.0.1"
        fields['zmq_pub_ip'] = "127.0.0.1"
        fields['dp_comm_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            'spgw_network', o, o, 'dp_comm_ip')
        fields['cp_comm_ip'] = self.get_ip_address_from_peer_service_instance(
            'spgw_network', "VSPGWCTenant", o, 'cp_comm_ip')
        fields['fpc_ip'] = "127.0.0.1"
        fields['cp_nb_server_ip'] = "127.0.0.1"

        # for cp_config.cfg file
        fields['s1u_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            's1u_network', o, o, 's1u_ip')
        fields['sgi_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            'sgi_network', o, o, 'sgi_ip')

        # for static_arp.cfg file
        fields['as_sgi_ip'] = self.get_ip_address_from_peer_service_instance(
            'sgi_network', "VENBServiceInstance", o, 'as_sgi_ip')
        fields['as_sgi_mac'] = self.get_mac_address_from_peer_service_instance(
            'sgi_network', "VENBServiceInstance", o, 'as_sgi_mac')
        fields['enb_s1u_ip'] = self.get_ip_address_from_peer_service_instance(
            's1u_network', "VENBServiceInstance", o, 'enb_s1u_ip')
        fields['enb_s1u_mac'] = self.get_mac_address_from_peer_service_instance(
            's1u_network', "VENBServiceInstance", o, 'enb_s1u_mac')

        return fields

    def get_values_for_CORD_5_0(self, o):
        fields = {}
        fields['cord_version'] = "5.0"
        fields['blueprint'] = "cord_5_0_blueprint"

        # for interface.cfg file
        fields['zmq_sub_ip'] = "127.0.0.1"
        fields['zmq_pub_ip'] = "127.0.0.1"
        fields['dp_comm_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            'spgw_network', o, o, 'dp_comm_ip')
        fields['cp_comm_ip'] = self.get_ip_address_from_peer_service_instance(
            'spgw_network', "VSPGWCTenant", o, 'cp_comm_ip')
        fields['fpc_ip'] = "127.0.0.1"
        fields['cp_nb_server_ip'] = "127.0.0.1"

        # for cp_config.cfg file
        fields['s1u_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            'flat_network_s1u', o, o, 's1u_ip')
        fields['sgi_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            'sgi_network', o, o, 'sgi_ip')

        # for static_arp.cfg file
        internetemulator_flag = self.has_instance("InternetEmulatorServiceInstance", o)
        if (internetemulator_flag):
            fields['as_sgi_ip'] = self.get_ip_address_from_peer_service_instance('sgi_network', "InternetEmulatorServiceInstance", o, 'as_sgi_ip')
            fields['as_sgi_mac'] = self.get_mac_address_from_peer_service_instance('sgi_network', "InternetEmulatorServiceInstance", o, 'as_sgi_mac')
        else:
            fields['as_sgi_ip'] = o.appserver_ip_addr
            fields['as_sgi_mac'] = o.appserver_mac_addr
        fields['enb_s1u_ip'] = o.enodeb_ip_addr # write down eNB IP address manually (S1U)
        fields['enb_s1u_mac'] = o.enodeb_mac_addr # write down eNB MAC address manually (S1U)

        return fields

    def has_instance(self, sitype, o):
        try:
            i = self.get_peer_serviceinstance_of_type(sitype, o)
        except ServiceGraphException:
            self.log.info("Missing in ServiceInstance graph",
                          serviceinstance=sitype)
            return False

        return i.leaf_model.instance_id

    def find_first_blueprint_subgraph(self, blueprints, adj_set):
        found_blueprint = None
        for blueprint in blueprints:
            found = True

            for node in blueprint['graph']:
                if node['name'] not in adj_set:
                    found = False
                    break
                try:
                    links = node['links']
                except KeyError:
                    links = []

                for link in links:
                    if link['name'] not in adj_set[node['name']]:
                        found = False
                        break
                if not found:
                    break

            if found:
                found_blueprint = blueprint['name']
                break

        return found_blueprint

    def check_instance_dependencies(self, blueprints, blueprint_name, o):
        blueprint = next(
                b for b in blueprints if b['name'] == blueprint_name)
        node = next(n for n in blueprint['graph'] if n['name'] == o.leaf_model_name)
        for link in node['links']:
            flag = self.has_instance(link['name'], o)
            if not flag:
                self.defer_sync('%s does not have an instance. Deferring synchronization.'%link['name'])
            
    def get_blueprint_and_check_dependencies(self, o):
        blueprints = Config().get('blueprints')

        adj_set = self.adj_set_of_service_graph(o)
        blueprint_name = self.find_first_blueprint_subgraph(blueprints, adj_set)
        if blueprint_name:
            self.check_instance_dependencies(blueprints, blueprint_name, o)

        ret_blueprint = 'manual' if not blueprint_name else blueprint_name
        return ret_blueprint

    def get_peer_serviceinstance_of_type(self, sitype, o):

        global_list = self.get_all_instances_in_graph(o)

        try:
            peer_service = next(p for p in global_list if p.leaf_model_name == sitype)

        except StopIteration:
            self.log.error(
                'Could not find service type in service graph', service_type=sitype, object=o)
            raise ServiceGraphException(
                "Synchronization failed due to incomplete service graph")

        return peer_service

    def has_instance_in_list(self, list, o):
        for instance in list:
            if instance.leaf_model_name == o.leaf_model_name:
                return True

        return False

    def get_all_instances_in_graph(self, o):

        to_search_list = self.get_one_hop_instances_in_graph(o)
        result_list = []

        while len(to_search_list) > 0:
            tmp_obj = to_search_list[0]
            to_search_list.remove(tmp_obj)
            tmp_list = self.get_one_hop_instances_in_graph(tmp_obj)

            for index_obj in tmp_list:
                if (not self.has_instance_in_list(to_search_list, index_obj)) and (not self.has_instance_in_list(result_list, index_obj)):
                    to_search_list.append(index_obj)

            result_list.append(tmp_obj)
        return result_list

    def get_one_hop_instances_in_graph(self, o):
        instance_list = []

        # 1 hop forward and backward
        prov_links = ServiceInstanceLink.objects.filter(subscriber_service_instance_id=o.id)
        subs_links = ServiceInstanceLink.objects.filter(provider_service_instance_id=o.id)

        # add instances located in 1 hop into instance_list
        for tmp_link1 in prov_links:
            if not self.has_instance_in_list(instance_list, tmp_link1.provider_service_instance):
                instance_list.append(tmp_link1.provider_service_instance)

        for tmp_link1 in subs_links:
            if not self.has_instance_in_list(instance_list, tmp_link1.subscriber_service_instance):
                instance_list.append(tmp_link1.subscriber_service_instance)

        return instance_list


    # Maybe merge the two pairs of functions into one, with an address type "mac" or "ip" - SB
    def get_ip_address_from_peer_service_instance(self, network_name, sitype, o, parameter=None):
        peer_si = self.get_peer_serviceinstance_of_type(sitype, o)
        return self.get_ip_address_from_peer_service_instance_instance(network_name, peer_si, o, parameter)

    def get_mac_address_from_peer_service_instance(self, network_name, sitype, o, parameter=None):
        peer_si = self.get_peer_serviceinstance_of_type(sitype, o)
        return self.get_mac_address_from_peer_service_instance_instance(network_name, peer_si, o, parameter)

    def get_ip_address_from_peer_service_instance_instance(self, network_name, peer_si, o, parameter=None):
        try:
            net_id = self.get_network_id(network_name)
            ins_id = peer_si.leaf_model.instance_id
            ip_address = Port.objects.get(
                network_id=net_id, instance_id=ins_id).ip
        except Exception:
            self.log.error("Failed to fetch parameter",
                           parameter=parameter,
                           network_name=network_name)
            self.defer_sync(o, "Waiting for parameters to become available")

        return ip_address

    def get_mac_address_from_peer_service_instance_instance(self, network_name, peer_si, o, parameter):
        try:
            net_id = self.get_network_id(network_name)
            ins_id = peer_si.leaf_model.instance_id
            mac_address = Port.objects.get(
                network_id=net_id, instance_id=ins_id).mac

        except Exception:
            self.log.error("Failed to fetch parameter to get MAC",
                           parameter=parameter, network_name=network_name)
            self.defer_sync(o, "Waiting for parameters to become available")

        return mac_address

    # To get each network id
    def get_network_id(self, network_name):
        return Network.objects.get(name=network_name).id

