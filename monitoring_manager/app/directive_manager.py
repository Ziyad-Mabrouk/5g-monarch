from app.logger import setup_logger
from app.orchestrator import NFVOrchestratorManager
import requests
from requests.models import Response


class DirectiveManager:
    def __init__(self, nfv_orchestrator: NFVOrchestratorManager):
        self.logger = setup_logger("directive_manager")
        self.nfv_orchestrator = nfv_orchestrator

    def process_directive(self, directive):
        self.logger.info("Processing directive: %s", directive)
        kpi_name = directive["kpi_name"]
        if kpi_name == "slice_throughput":
            return self.process_slice_throughput_directive(directive)
        
        elif kpi_name == "mac_throughput":
            return self.process_mac_throughput_directive(directive)
        
        elif kpi_name == "number_ues":
            return self.process_number_ues_directive(directive)
        
        elif kpi_name == "saturation_percentage":
            return self.process_saturation_percentage_directive(directive)

        else:
            self.logger.error(f"KPI {kpi_name} not supported")
            raise NotImplementedError(f"KPI {kpi_name} not supported")

    def process_slice_throughput_directive(self, directive):
        self.logger.info("Processing slice throughput directive: %s", directive)

        if directive["action"] == "create":
            # for now, we will just install pre-configured MDE and KPI Computation
            # if NFV orchestrator supports it, we can change the configuration MDE and KPI computation components
            # using the information in the directive
            self.logger.info("Installing Core MDE")
            response_mde = self.nfv_orchestrator.core_mde_install()
            if response_mde.status_code != 200:
                self.logger.error("Error installing Core MDE: %s", response_mde.text)
                return response_mde

            self.logger.info("Installing Core KPI Computation")
            response_kpi = self.nfv_orchestrator.core_kpi_computation_install()
            if response_kpi.status_code != 200:
                self.logger.error("Error installing Core KPI Computation: %s", response_kpi.text)
                return response_kpi

            self.logger.info("Both Core MDE and KPI Computation installed successfully.")
            return self._create_success_response(action="installed")

        elif directive["action"] == "delete":
            self.logger.info("Uninstalling Core MDE")
            response_mde = self.nfv_orchestrator.core_mde_uninstall()
            if response_mde.status_code != 200:
                self.logger.error("Error uninstalling Core MDE: %s", response_mde.text)
                return response_mde

            self.logger.info("Uninstalling Core KPI Computation")
            response_kpi = self.nfv_orchestrator.core_kpi_computation_uninstall()
            if response_kpi.status_code != 200:
                self.logger.error("Error uninstalling Core KPI Computation: %s", response_kpi.text)
                return response_kpi

            self.logger.info("Both Core MDE and KPI Computation uninstalled successfully.")
            return self._create_success_response(action="deleted")
        
    def process_mac_throughput_directive(self, directive):
        self.logger.info("Processing MAC throughput directive: %s", directive)

        if directive["action"] == "create":
            # for now, we will just install pre-configured MDE and KPI Computation
            # if NFV orchestrator supports it, we can change the configuration MDE and KPI computation components
            # using the information in the directive
            self.logger.info("Installing RAN MDE")
            response_mde = self.nfv_orchestrator.ran_mde_install()
            if response_mde.status_code != 200:
                self.logger.error("Error installing RAN MDE: %s", response_mde.text)
                return response_mde

            self.logger.info("Installing RAN KPI Computation")
            response_kpi = self.nfv_orchestrator.ran_kpi_computation_install()
            if response_kpi.status_code != 200:
                self.logger.error("Error installing RAN KPI Computation: %s", response_kpi.text)
                return response_kpi

            self.logger.info("Both RAN MDE and KPI Computation installed successfully.")
            return self._create_success_response(action="installed")

        elif directive["action"] == "delete":
            self.logger.info("Uninstalling RAN MDE")
            response_mde = self.nfv_orchestrator.ran_mde_uninstall()
            if response_mde.status_code != 200:
                self.logger.error("Error uninstalling RAN MDE: %s", response_mde.text)
                return response_mde

            self.logger.info("Uninstalling RAN KPI Computation")
            response_kpi = self.nfv_orchestrator.ran_kpi_computation_uninstall()
            if response_kpi.status_code != 200:
                self.logger.error("Error uninstalling RAN KPI Computation: %s", response_kpi.text)
                return response_kpi

            self.logger.info("Both RAN MDE and KPI Computation uninstalled successfully.")
            return self._create_success_response(action="deleted")
        
    def process_number_ues_directive(self, directive):
        self.logger.info("Processing Number of connected UEs directive: %s", directive)

        if directive["action"] == "create":
            # for now, we will just install pre-configured MDE and KPI Computation
            # if NFV orchestrator supports it, we can change the configuration MDE and KPI computation components
            # using the information in the directive
            self.logger.info("Installing RAN MDE")
            response_mde = self.nfv_orchestrator.ran_mde_install()
            if response_mde.status_code != 200:
                self.logger.error("Error installing RAN MDE: %s", response_mde.text)
                return response_mde

            self.logger.info("Installing RAN KPI Computation")
            response_kpi = self.nfv_orchestrator.ran_kpi_computation_install()
            if response_kpi.status_code != 200:
                self.logger.error("Error installing RAN KPI Computation: %s", response_kpi.text)
                return response_kpi

            self.logger.info("Both RAN MDE and KPI Computation installed successfully.")
            return self._create_success_response(action="installed")

        elif directive["action"] == "delete":
            self.logger.info("Uninstalling RAN MDE")
            response_mde = self.nfv_orchestrator.ran_mde_uninstall()
            if response_mde.status_code != 200:
                self.logger.error("Error uninstalling RAN MDE: %s", response_mde.text)
                return response_mde

            self.logger.info("Uninstalling RAN KPI Computation")
            response_kpi = self.nfv_orchestrator.ran_kpi_computation_uninstall()
            if response_kpi.status_code != 200:
                self.logger.error("Error uninstalling RAN KPI Computation: %s", response_kpi.text)
                return response_kpi

            self.logger.info("Both RAN MDE and KPI Computation uninstalled successfully.")
            return self._create_success_response(action="deleted")
        
    def process_saturation_percentage_directive(self, directive):
        self.logger.info("Processing PRB saturation percentage directive: %s", directive)

        if directive["action"] == "create":
            # for now, we will just install pre-configured MDE and KPI Computation
            # if NFV orchestrator supports it, we can change the configuration MDE and KPI computation components
            # using the information in the directive
            self.logger.info("Installing RAN MDE")
            response_mde = self.nfv_orchestrator.ran_mde_install()
            if response_mde.status_code != 200:
                self.logger.error("Error installing RAN MDE: %s", response_mde.text)
                return response_mde

            self.logger.info("Installing RAN KPI Computation")
            response_kpi = self.nfv_orchestrator.ran_kpi_computation_install()
            if response_kpi.status_code != 200:
                self.logger.error("Error installing RAN KPI Computation: %s", response_kpi.text)
                return response_kpi

            self.logger.info("Both RAN MDE and KPI Computation installed successfully.")
            return self._create_success_response(action="installed")

        elif directive["action"] == "delete":
            self.logger.info("Uninstalling RAN MDE")
            response_mde = self.nfv_orchestrator.ran_mde_uninstall()
            if response_mde.status_code != 200:
                self.logger.error("Error uninstalling RAN MDE: %s", response_mde.text)
                return response_mde

            self.logger.info("Uninstalling RAN KPI Computation")
            response_kpi = self.nfv_orchestrator.ran_kpi_computation_uninstall()
            if response_kpi.status_code != 200:
                self.logger.error("Error uninstalling RAN KPI Computation: %s", response_kpi.text)
                return response_kpi

            self.logger.info("Both RAN MDE and KPI Computation uninstalled successfully.")
            return self._create_success_response(action="deleted")


    def _create_success_response(self, action="installed"):
        response = Response()
        response.status_code = 200
        response._content = f"Both MDE and KPI Computation {action} successfully.".encode("utf-8")
        response.encoding = "utf-8"
        return response
