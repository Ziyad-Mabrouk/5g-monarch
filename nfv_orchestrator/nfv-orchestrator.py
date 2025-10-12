from flask import Flask, request, jsonify
import os
import logging
import subprocess
import json

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))


def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(ch)

    return logger


class DummyNFVOrchestrator:
    def __init__(self):
        self.logger = setup_logger("nfv_orchestrator")
        self.logger.info("NFV Orchestrator started")
        self.app = Flask(__name__)

        self._set_routes()

    def _set_routes(self):
        self.app.add_url_rule("/core_mde/install", "core_mde_install", self.core_mde_install, methods=["POST"])
        self.app.add_url_rule("/core_mde/uninstall", "core_mde_uninstall", self.core_mde_uninstall, methods=["POST"])
        self.app.add_url_rule("/core_mde/check", "core_mde_check", self.core_mde_check, methods=["POST"])
        self.app.add_url_rule("/ran_mde/install", "ran_mde_install", self.ran_mde_install, methods=["POST"])
        self.app.add_url_rule("/ran_mde/uninstall", "ran_mde_uninstall", self.ran_mde_uninstall, methods=["POST"])
        self.app.add_url_rule("/ran_mde/check", "ran_mde_check", self.ran_mde_check, methods=["POST"])
        self.app.add_url_rule(
            "/core_kpi_computation/install", "core_kpi_computation_install", self.core_kpi_computation_install, methods=["POST"]
        )
        self.app.add_url_rule(
            "/core_kpi_computation/uninstall", "core_kpi_computation_uninstall", self.core_kpi_computation_uninstall, methods=["POST"]
        )
        self.app.add_url_rule(
            "/core_kpi_computation/check", "core_kpi_computation_check", self.core_kpi_computation_check, methods=["POST"]
        )
        self.app.add_url_rule(
            "/ran_kpi_computation/install", "ran_kpi_computation_install", self.ran_kpi_computation_install, methods=["POST"]
        )
        self.app.add_url_rule(
            "/ran_kpi_computation/uninstall", "ran_kpi_computation_uninstall", self.ran_kpi_computation_uninstall, methods=["POST"]
        )
        self.app.add_url_rule(
            "/ran_kpi_computation/check", "ran_kpi_computation_check", self.ran_kpi_computation_check, methods=["POST"]
        )
        self.app.add_url_rule("/api/health", "check_health", self.check_health, methods=["GET"])

    def core_mde_install(self):
        return_value = os.system(f"{WORKING_DIR}/../mde/core/install.sh")
        if return_value != 0:
            return jsonify({"status": "error", "message": "Core MDE installation failed"}), 500
        else:
            return jsonify({"status": "success", "message": "Core MDE installed"}), 200

    def core_mde_uninstall(self):
        return_value = os.system(f"{WORKING_DIR}/../mde/core/uninstall.sh")
        if return_value != 0:
            return jsonify({"status": "error", "message": "Core MDE uninstallation failed"}), 500
        else:
            return jsonify({"status": "success", "message": "Core MDE uninstalled"}), 200

    def core_mde_check(self):
        try:
            # Run the command and capture output
            result = subprocess.run(
                [f"{WORKING_DIR}/../mde/core/check-mde.sh"],
                capture_output=True,
                text=True,
                check=True
            )
            return jsonify({"status": "success", "message": "Core MDE test success", "output": result.stdout}), 200
        except subprocess.CalledProcessError as e:
            return jsonify({"status": "error", "message": "Core MDE test failed", "output": e.stderr}), 500
        
    def ran_mde_install(self):
        return_value = os.system(f"{WORKING_DIR}/../mde/ran/install.sh")
        if return_value != 0:
            return jsonify({"status": "error", "message": "RAN MDE installation failed"}), 500
        else:
            return jsonify({"status": "success", "message": "RAN MDE installed"}), 200

    def ran_mde_uninstall(self):
        return_value = os.system(f"{WORKING_DIR}/../mde/ran/uninstall.sh")
        if return_value != 0:
            return jsonify({"status": "error", "message": "RAN MDE uninstallation failed"}), 500
        else:
            return jsonify({"status": "success", "message": "RAN MDE uninstalled"}), 200

    def ran_mde_check(self):
        try:
            # Run the command and capture output
            result = subprocess.run(
                [f"{WORKING_DIR}/../mde/ran/check-mde.sh"],
                capture_output=True,
                text=True,
                check=True
            )
            return jsonify({"status": "success", "message": "RAN MDE test success", "output": result.stdout}), 200
        except subprocess.CalledProcessError as e:
            return jsonify({"status": "error", "message": "RAN MDE test failed", "output": e.stderr}), 500

    def core_kpi_computation_install(self):
        return_value = os.system(f"{WORKING_DIR}/../kpi_computation/core/install.sh")
        if return_value != 0:
            return jsonify({"status": "error", "message": "Core KPI Computation installation failed"}), 500
        else:
            return jsonify({"status": "success", "message": "Core KPI Computation installed"}), 200

    def core_kpi_computation_uninstall(self):
        return_value = os.system(f"{WORKING_DIR}/../kpi_computation/core/uninstall.sh")
        if return_value != 0:
            return jsonify({"status": "error", "message": "Core KPI Computation uninstallation failed"}), 500
        else:
            return jsonify({"status": "success", "message": "Core KPI Computation uninstalled"}), 200

    def core_kpi_computation_check(self):
        try:
            # Run the command and capture output
            result = subprocess.run(
                [f"{WORKING_DIR}/../kpi_computation/core/check-kpi.sh"],
                capture_output=True,
                text=True,
                check=True
            )
            return jsonify({"status": "success", "message": "Core KPI test success", "output": result.stdout}), 200
        except subprocess.CalledProcessError as e:
            return jsonify({"status": "error", "message": "Core KPI test failed", "output": e.stderr}), 500
        
    def ran_kpi_computation_install(self):
        return_value = os.system(f"{WORKING_DIR}/../kpi_computation/ran/install.sh")
        if return_value != 0:
            return jsonify({"status": "error", "message": "RAN KPI Computation installation failed"}), 500
        else:
            return jsonify({"status": "success", "message": "RAN KPI Computation installed"}), 200

    def ran_kpi_computation_uninstall(self):
        return_value = os.system(f"{WORKING_DIR}/../kpi_computation/ran/uninstall.sh")
        if return_value != 0:
            return jsonify({"status": "error", "message": "RAN KPI Computation uninstallation failed"}), 500
        else:
            return jsonify({"status": "success", "message": "RAN KPI Computation uninstalled"}), 200

    def ran_kpi_computation_check(self):
        try:
            # Run the command and capture output
            result = subprocess.run(
                [f"{WORKING_DIR}/../kpi_computation/ran/check-kpi.sh"],
                capture_output=True,
                text=True,
                check=True
            )
            return jsonify({"status": "success", "message": "RAN KPI test success", "output": result.stdout}), 200
        except subprocess.CalledProcessError as e:
            return jsonify({"status": "error", "message": "RAN KPI test failed", "output": e.stderr}), 500

    def check_health(self):
        return jsonify({"status": "success", "message": "NFV Orchestrator is healthy"}), 200

    def run(self, debug, port, host):
        self.app.run(debug=debug, port=port, host=host)


if __name__ == "__main__":
    nfvo = DummyNFVOrchestrator()
    nfvo.run(debug=True, port=6001, host="0.0.0.0")
