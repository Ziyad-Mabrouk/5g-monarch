from app.logger import setup_logger
from app.service_orchestrator import ServiceOrchestratorManager


class TranslationManager:
    def __init__(self, service_orchestrator: ServiceOrchestratorManager):
        self.logger = setup_logger("translation_manager")
        self.service_orchestrator = service_orchestrator

    def translate_request(self, request, request_id):
        self.logger.info("Translating request...")
        kpi_name = request["kpi"]["kpi_name"]

        if kpi_name == "slice_throughput":
            components = self.translate_slice_throughput(request)

        elif kpi_name == "mac_throughput":
            components = self.translate_mac_throughput(request)

        elif kpi_name == "number_ues":
            components = self.translate_number_ues(request)

        elif kpi_name == "saturation_percentage":
            components = self.translate_saturation_percentage(request)

        else:
            raise NotImplementedError(f"KPI '{kpi_name}' is not supported")

        directive = {
            "request_id": request_id,
            "kpi_name": kpi_name,
            "action": "create",
            "components": components,
            "interval": request["monitoring_interval"]["interval_seconds"],
        }

        self.logger.debug(f"Translated directive: {directive}")
        return directive

    def translate_slice_throughput(self, request):
        """
        Translates a slice throughput request into metrics from SMF and UPF to monitor.
        3GPP 28.554 Section 6.3.2 and 6.3.3
        """
        self.logger.info("Translating slice throughput request...")
        snssais = request["kpi"]["sub_counter"]["sub_counter_ids"]
        self.logger.info(f"NSSAIs: {snssais}")

        components_to_monitor = []

        # get pod_info for the NFs by interacting with the service orchestrator
        for snssai in snssais:
            pod_infos = self.service_orchestrator.get_slice_components(snssai)
            self.logger.info(f"Pod info for SNSSAI {snssai}: {pod_infos}")

        for pod_info in pod_infos:
            component_info = {}
            if pod_info["nf"] == "smf":
                component_info["type"] = "pod"
                component_info["nf"] = "smf"
                component_info["nss"] = pod_info["nss"]
                component_info["pod_name"] = pod_info["name"]
                component_info["pod_ip"] = pod_info["pod_ip"]
                component_info["metrics"] = ["fivegs_smffunction_sm_seid_session"]
                components_to_monitor.append(component_info)

            elif pod_info["nf"] == "upf":
                component_info["type"] = "pod"
                component_info["nf"] = "upf"
                component_info["nss"] = pod_info["nss"]
                component_info["pod_name"] = pod_info["name"]
                component_info["pod_ip"] = pod_info["pod_ip"]
                component_info["metrics"] = [
                    "fivegs_ep_n3_gtp_outdatavolumen3upf_seid_total",
                    "fivegs_ep_n3_gtp_outdatavolumen3upf_seid_total",
                ]
                pod_info["metrics"] = [
                    "fivegs_ep_n3_gtp_outdatavolumen3upf_seid_total",
                    "fivegs_ep_n3_gtp_outdatavolumen3upf_seid_total",
                ]
                components_to_monitor.append(component_info)

        self.logger.debug(f"Components to monitor: {components_to_monitor}")
        return components_to_monitor

    def translate_mac_throughput(self, request):
        """
        Translates a MAC throughput request into metrics from gNB to monitor.
        """
        self.logger.info("Translating MAC throughput request...")

        components_to_monitor = []

        # get pod_info for the gNB by interacting with the service orchestrator
        pod_info = self.service_orchestrator.get_gnb()
        self.logger.info(f"Pod info for gNB: {pod_info}")

        component_info = {}
        component_info["type"] = "pod"
        component_info["nf"] = "gnb"
        component_info["nss"] = "edge"
        component_info["pod_name"] = pod_info["name"]
        component_info["pod_ip"] = pod_info["pod_ip"]
        component_info["metrics"] = [
            "oai_gnb_mac_tx_bytes",
            "oai_gnb_mac_rx_bytes"
            ]
        components_to_monitor.append(component_info)

        self.logger.debug(f"Components to monitor: {components_to_monitor}")
        return components_to_monitor
    
    def translate_number_ues(self, request):
        """
        Translates a Number of connected UEs request into metrics from gNB to monitor.
        """
        self.logger.info("Translating Number of connected UEs request...")

        components_to_monitor = []

        # get pod_info for the gNB by interacting with the service orchestrator
        pod_info = self.service_orchestrator.get_gnb()
        self.logger.info(f"Pod info for gNB: {pod_info}")

        component_info = {}
        component_info["type"] = "pod"
        component_info["nf"] = "gnb"
        component_info["nss"] = "edge"
        component_info["pod_name"] = pod_info["name"]
        component_info["pod_ip"] = pod_info["pod_ip"]
        component_info["metrics"] = [
            "oai_gnb_mac_tx_bytes"
            ]
        components_to_monitor.append(component_info)

        self.logger.debug(f"Components to monitor: {components_to_monitor}")
        return components_to_monitor
    
    def translate_saturation_percentage(self, request):
        """
        Translates a PRB Saturaion percentage request into metrics from gNB to monitor.
        """
        self.logger.info("Translating PRB Saturaion percentage request...")

        components_to_monitor = []

        # get pod_info for the gNB by interacting with the service orchestrator
        pod_info = self.service_orchestrator.get_gnb()
        self.logger.info(f"Pod info for gNB: {pod_info}")

        component_info = {}
        component_info["type"] = "pod"
        component_info["nf"] = "gnb"
        component_info["nss"] = "edge"
        component_info["pod_name"] = pod_info["name"]
        component_info["pod_ip"] = pod_info["pod_ip"]
        component_info["metrics"] = [
            "oai_gnb_mac_nprb",
            "oai_gnb_l1_total_prbs"
            ]
        components_to_monitor.append(component_info)

        self.logger.debug(f"Components to monitor: {components_to_monitor}")
        return components_to_monitor