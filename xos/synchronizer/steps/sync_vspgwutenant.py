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


class SyncVSPGWUTenant(SyncInstanceUsingAnsible):
    observes = VSPGWUTenant
    template_name = "vspgwutenant_playbook.yaml"
    service_key_name = "/opt/xos/configurations/mcord/mcord_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncVSPGWUTenant, self).__init__(*args, **kwargs)

    def get_extra_attributes(self, o):

        scenario = self.get_scenario(o)

        if scenario == 'normal_scenario':
            return self.get_values_for_normal_scenario(o)
        elif scenario == 'normal_scenario_without_sdncontroller':
            return self.get_values_for_normal_scenario_wo_sdncontroller(o)
        elif scenario == 'emulator_scenario':
            return self.get_values_for_emulator_scenario(o)
        elif scenario == 'emulator_scenario_without_sdncontroller':
            return self.get_values_for_emulator_scenario_wo_sdncontroller(o)
        else:
            return self.get_extra_attributes_for_manual(o)

    # fields for manual case
    def get_extra_attributes_for_manual(self, o):
        fields = {}
        fields['scenario'] = self.get_scenario(o)
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

    def get_values_for_normal_scenario(self, o):
        fields = {}
        fields['scenario'] = "normal_scenario"
        # for interface.cfg file
        fields['zmq_sub_ip'] = self.get_ip_address_from_peer_service_instance(
            'sbi_network', "SDNControllerServiceInstance", 'zmq_sub_ip')
        fields['zmq_pub_ip'] = self.get_ip_address_from_peer_service_instance(
            'sbi_network', "SDNControllerServiceInstance", 'zmq_pub_ip')
        fields['dp_comm_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            'sbi_network', o, 'dp_comm_ip')
        fields['cp_comm_ip'] = self.get_ip_address_from_peer_service_instance(
            'nbi_network', "VSPGWCTenant", 'cp_comm_ip')
        fields['fpc_ip'] = self.get_ip_address_from_peer_service_instance(
            'nbi_network', "SDNControllerServiceInstance", 'fpc_ip')
        fields['cp_nb_server_ip'] = self.get_ip_address_from_peer_service_instance(
            'nbi_network', "VSPGWCTenant", 'cp_nb_server_ip')

        # for dp_config.cfg file
        fields['s1u_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            's1u_network', o, 's1u_ip')
        fields['sgi_ip'] = self.get_ip_address_from_peer_service_instance(
            'sgi_network', "VSPGWUTenant", 'sgi_ip')

        # for static_arp.cfg file
        fields['as_sgi_ip'] = self.get_ip_address('sgi_network', InternetEmulatorServiceInstance, 'as_sgi_ip')
        fields['as_sgi_mac'] = self.get_mac_address('sgi_network', InternetEmulatorServiceInstance, 'as_sgi_mac')
        fields['enb_s1u_ip'] = self.get_ip_address('s1u_network', VENBServiceInstance, 'enb_s1u_ip')
        fields['enb_s1u_mac'] = self.get_mac_address('s1u_network', VENBServiceInstance, 'enb_s1u_mac')

        return fields

    def get_values_for_normal_scenario_wo_sdncontroller(self, o):
        fields = {}
        fields['scenario'] = "normal_scenario_without_sdncontroller"
        # for interface.cfg file
        fields['zmq_sub_ip'] = "127.0.0.1"
        fields['zmq_pub_ip'] = "127.0.0.1"
        fields['dp_comm_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            'spgw_network', o, 'dp_comm_ip')
        fields['cp_comm_ip'] = self.get_ip_address_from_peer_service_instance(
            'spgw_network', "VSPGWCTenant", 'cp_comm_ip')
        fields['fpc_ip'] = "127.0.0.1"
        fields['cp_nb_server_ip'] = "127.0.0.1"

        # for cp_config.cfg file
        fields['s1u_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            's1u_network', o, 's1u_ip')
        fields['sgi_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            'sgi_network', o, 'sgi_ip')

        # for static_arp.cfg file
        fields['as_sgi_ip'] = self.get_ip_address('sgi_network', InternetEmulatorServiceInstance, 'as_sgi_ip')
        fields['as_sgi_mac'] = self.get_mac_address('sgi_network', InternetEmulatorServiceInstance, 'as_sgi_mac')
        fields['enb_s1u_ip'] = self.get_ip_address('s1u_network', VENBServiceInstance, 'enb_s1u_ip')
        fields['enb_s1u_mac'] = self.get_mac_address('s1u_network', VENBServiceInstance, 'enb_s1u_mac')

        return fields

    def get_values_for_emulator_scenario(self, o):
        fields = {}
        fields['scenario'] = "emulator_scenario"
        # for interface.cfg file
        fields['zmq_sub_ip'] = self.get_ip_address_from_peer_service_instance(
            'sbi_network', "SDNControllerServiceInstance", 'zmq_sub_ip')
        fields['zmq_pub_ip'] = self.get_ip_address_from_peer_service_instance(
            'sbi_network', "SDNControllerServiceInstance", 'zmq_pub_ip')
        fields['dp_comm_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            'sbi_network', o, 'dp_comm_ip')
        fields['cp_comm_ip'] = self.get_ip_address_from_peer_service_instance(
            'nbi_network', "VSPGWCTenant", 'cp_comm_ip')
        fields['fpc_ip'] = self.get_ip_address_from_peer_service_instance(
            'nbi_network', "SDNControllerServiceInstance", 'fpc_ip')
        fields['cp_nb_server_ip'] = self.get_ip_address_from_peer_service_instance(
            'nbi_network', "VSPGWCTenant", 'cp_nb_server_ip')

        # for dp_config.cfg file
        fields['s1u_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            's1u_network', o, 's1u_ip')
        fields['sgi_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            'sgi_network', o, 'sgi_ip')

        # for static_arp.cfg file
        fields['as_sgi_ip'] = self.get_ip_address('sgi_network', VENBServiceInstance, 'as_sgi_ip')
        fields['as_sgi_mac'] = self.get_mac_address('sgi_network', VENBServiceInstance, 'as_sgi_mac')
        fields['enb_s1u_ip'] = self.get_ip_address('s1u_network', VENBServiceInstance, 'enb_s1u_ip')
        fields['enb_s1u_mac'] = self.get_mac_address('s1u_network', VENBServiceInstance, 'enb_s1u_mac')

        return fields

    def get_values_for_emulator_scenario_wo_sdncontroller(self, o):
        fields = {}
        fields['scenario'] = "emulator_scenario_without_sdncontroller"
        # for interface.cfg file
        fields['zmq_sub_ip'] = "127.0.0.1"
        fields['zmq_pub_ip'] = "127.0.0.1"
        fields['dp_comm_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            'spgw_network', o, 'dp_comm_ip')
        fields['cp_comm_ip'] = self.get_ip_address_from_peer_service_instance(
            'spgw_network', "VSPGWCTenant", 'cp_comm_ip')
        fields['fpc_ip'] = "127.0.0.1"
        fields['cp_nb_server_ip'] = "127.0.0.1"

        # for cp_config.cfg file
        fields['s1u_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            's1u_network', o, 's1u_ip')
        fields['sgi_ip'] = self.get_ip_address_from_peer_service_instance_instance(
            'sgi_network', o, 'sgi_ip')

        # for static_arp.cfg file
        fields['as_sgi_ip'] = self.get_ip_address('sgi_network', VENBServiceInstance, 'as_sgi_ip')
        fields['as_sgi_mac'] = self.get_mac_address('sgi_network', VENBServiceInstance, 'as_sgi_mac')
        fields['enb_s1u_ip'] = self.get_ip_address('s1u_network', VENBServiceInstance, 'enb_s1u_ip')
        fields['enb_s1u_mac'] = self.get_mac_address('s1u_network', VENBServiceInstance, 'enb_s1u_mac')

        return fields

    def has_instance(self, sitype, o):
        i = self.get_peer_serviceinstance_of_type(sitype, o)
        if not i:
            self.log.info("Missing in ServiceInstance graph",
                          serviceinstance=sitype)
            return False

        return i.instance_id

    # Which scenario does it use among Spirent or NG4T?
    def get_scenario(self, o):
        # try get vENB instance: one of both Spirent and NG4T
        venb_flag = self.has_instance("VENBServiceInstance", o)
        vmme_flag = self.has_instance("VMMETenant", o)
        sdncontroller_flag = self.has_instance(
            "SDNControllerServiceInstance", o)
        vspgwu_flag = self.has_instance("VSPGWUTenant", o)
        internetemulator_flag = self.has_instance(
            "SDNControllerServiceInstance", o)

        # wait until vspgwu and env are comming up
        if (not vspgwu_flag):
            self.defer_sync("Waiting for vSPGWU to come up")

        if (not venb_flag):
            self.defer_sync("Waiting for vENB to come up")

        if vmme_flag and venb_flag and sdncontroller_flag and vspgwu_flag and internetemulator_flag:
            return 'normal_scenario'

        if vmme_flag and venb_flag and (not sdncontroller_flag) and vspgwu_flag and internetemulator_flag:
            return 'normal_scenario_without_sdncontroller'

        if (not vmme_flag) and venb_flag and sdncontroller_flag and vspgwu_flag and (not internetemulator_flag):
            return 'emulator_scenario'

        if (not vmme_flag) and venb_flag and (not sdncontroller_flag) and vspgwu_flag and (not internetemulator_flag):
            return 'emulator_scenario_without_sdncontroller'

        return 'manual'

    def get_peer_serviceinstance_of_type(self, sitype, o):
        prov_link_set = ServiceInstanceLink.objects.filter(
            subscriber_service_instance_id=o.id)

        try:
            peer_service = next(
                p for p in prov_link_set if p.leaf_model_name == sitype)
        except StopIteration:
            sub_link_set = ServiceInstanceLink.objects.filter(
                provider_service_instance_id=o.id)
            try:
                peer_service = next(
                    s for s in sub_link_set if s.leaf_model_name == sitype)
            except StopIteration:
                self.log.error(
                    'Could not find service type in service graph', service_type=sitype, object=o)
                raise Exception(
                    "Synchronization failed due to incomplete service graph")

        return peer_service

    def get_ip_address_from_peer_service_instance(self, network_name, sitype, o, parameter=None):
        peer_si = self.get_peer_serviceinstance_of_type(sitype, o)
        return self.get_ip_address_for_peer_service_instance_instance(network_name, peer_si, parameter)

    def get_ip_address_from_peer_service_instance_instance(self, network_name, peer_si, parameter=None):
        try:
            net_id = self.get_network_id(network_name)
            ins_id = peer_si.instance_id
            ip_address = Port.objects.get(
                network_id=net_id, instance_id=ins_id).ip
        except Exception:
            ip_address = "error"
            self.log.error("Failed to fetch parameter to get IP", parameter = parameter, network_name = network_name)
            self.defer_sync("Waiting for parameters to become available")

        return ip_address

    def get_mac_address(self, network_name, service_instance, parameter):

        try:
            net_id = self.get_network_id(network_name)
            ins_id = self.get_instance_id(service_instance)
            mac_address = Port.objects.get(network_id=net_id, instance_id=ins_id).ip

        except Exception:
            mac_address = "error"
            self.log.error("Failed to fetch parameter to get MAC", parameter = parameter, network_name = network_name)
            self.defer_sync("Waiting for parameters to become available")

        return mac_address

    # To get each network id
    def get_network_id(self, network_name):
        return Network.objects.get(name=network_name).id
