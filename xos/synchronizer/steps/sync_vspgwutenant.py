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

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)


class ServiceGraphException(Exception):
    pass


class SyncVSPGWUTenant(SyncInstanceUsingAnsible):
    observes = VSPGWUTenant
    template_name = "vspgwutenant_playbook.yaml"
    service_key_name = "/opt/xos/configurations/mcord/mcord_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncVSPGWUTenant, self).__init__(*args, **kwargs)

    def get_extra_attributes(self, o):

        scenario = self.get_scenario(o)

        if scenario == 'cord_4_1_scenario':
            return self.get_values_for_CORD_4_1(o)
        elif scenario == 'cord_5_0_scenario':
            return self.get_values_for_CORD_5_0(o)
        else:
            return self.get_extra_attributes_for_manual(o)

    # fields for manual case
    def get_extra_attributes_for_manual(self, o):
        fields = {}
        fields['scenario'] = "manual"
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
        fields['scenario'] = "cord_4_1_scenario"
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
        fields['scenario'] = "cord_5_0_scenario"

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

    # Which scenario does it use among Spirent or NG4T?
    def get_scenario(self, o):
        # try get vENB instance: one of both Spirent and NG4T
        venb_flag = self.has_instance("VENBServiceInstance", o)
        vmme_flag = self.has_instance("VMMETenant", o)
        sdncontroller_flag = self.has_instance(
            "SDNControllerServiceInstance", o)
        vspgwc_flag = self.has_instance("VSPGWCTenant", o)
        internetemulator_flag = self.has_instance(
            "InternetEmulatorServiceInstance", o)
        vhss_flag = self.has_instance("VHSSTenant", o)
        hssdb_flag = self.has_instance("HSSDBServiceInstance", o)

        if (o.blueprint == "build") or (o.blueprint == "MCORD 4.1"):
            if not venb_flag:
                self.defer_sync(o, "Waiting for eNB image to become available")
            if not vspgwc_flag:
                self.defer_sync(o, "Waiting for SPGWC image to become available")
            return 'cord_4_1_scenario'

        if (o.blueprint == "mcord_5") or (o.blueprint == "MCORD 5"):
            if not hssdb_flag:
                self.defer_sync(o, "Waiting for HSS_DB image to become available")
            if not vhss_flag:
                self.defer_sync(o, "Waiting for vHSS image to become available")
            if not vmme_flag:
                self.defer_sync(o, "Waiting for vMME image to become available")
            if not vspgwc_flag:
                self.defer_sync(o, "Waiting for vSPGWC image to become available")
            return 'cord_5_0_scenario'

        return 'manual'

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
