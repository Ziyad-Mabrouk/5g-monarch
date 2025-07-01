#----------------------------------------------------------------------------
# Author: Niloy Saha
# Email: niloysaha.ns@gmail.com
# version ='1.0.0'
# ---------------------------------------------------------------------------
"""
Prometheus exporter which exports slice throughput KPI.
For use with the 5G-MONARCH project and Open5GS.
"""
from datetime import datetime, timedelta, timezone
import os
import logging
import time
import requests
import prometheus_client as prom
import argparse

from dotenv import load_dotenv

load_dotenv()
MONARCH_THANOS_URL = os.getenv("MONARCH_THANOS_URL")
DEFAULT_UPDATE_PERIOD = 1
UPDATE_PERIOD = int(os.environ.get('UPDATE_PERIOD', DEFAULT_UPDATE_PERIOD))
EXPORTER_PORT = 9000
TIME_RANGE = os.getenv("TIME_RANGE", "5s")


# Prometheus variables
SLICE_THROUGHPUT = prom.Gauge('slice_throughput', 'throughput per slice (bits/sec)', ['snssai', 'seid', 'direction'])
MAC_THROUGHPUT = prom.Gauge('mac_throughput', 'MAC throughput per UE RNTI (bits/sec)', ['rnti', 'direction'])
NUMBER_UES = prom.Gauge('number_ues', 'Number of connected UEs in the gNB')
SATURATION_PERCENTAGE = prom.Gauge('saturation_percentage', 'Percentage of total gNB PRBs currently scheduled (NPRB sum / total PRBs * 100)', ['rnti'])

# get rid of bloat
prom.REGISTRY.unregister(prom.PROCESS_COLLECTOR)
prom.REGISTRY.unregister(prom.PLATFORM_COLLECTOR)
prom.REGISTRY.unregister(prom.GC_COLLECTOR)

def query_prometheus(params, url):
    """
    Query Prometheus using requests and return value.
    params: The parameters for the Prometheus query.
    url: The URL of the Prometheus server.
    Returns: The result of the Prometheus query.
    """
    try:
        r = requests.get(url + '/api/v1/query', params)
        data = r.json()

        results = data["data"]["result"]
        return results
        
    except requests.exceptions.RequestException as e:
        log.error(f"Failed to query Prometheus: {e}")
    except (KeyError, IndexError, ValueError) as e:
        log.error(f"Failed to parse Prometheus response: {e}")
        log.warning("No data available!")

def get_slice_throughput_per_seid_and_direction(snssai, direction):
    """
    Queries both the SMF and UPF to get the throughput per SEID and direction.
    Returns a dictionary of the form {seid: value (bits/sec)}
    """
    time_range = TIME_RANGE
    throughput_per_seid = {}  # {seid: value (bits/sec)}

    direction_mapping = {
        "uplink": "indatavolumen3upf",
        "downlink": "outdatavolumen3upf"
    }

    if direction not in direction_mapping:
        log.error("Invalid direction")
        return

    query = f'sum by (seid) (rate(fivegs_ep_n3_gtp_{direction_mapping[direction]}_seid[{time_range}]) * on (seid) group_right sum(fivegs_smffunction_sm_seid_session{{snssai="{snssai}"}}) by (seid, snssai)) * 8'
    log.debug(query)
    params = {'query': query}
    results = query_prometheus(params, MONARCH_THANOS_URL)

    if results:
        for result in results:
            seid = result["metric"]["seid"]
            value = float(result["value"][1])
            throughput_per_seid[seid] = value

    return throughput_per_seid

def get_mac_throughput_per_rnti_and_direction(direction):
    """
    Returns throughput per UE RNTI for the specified direction: 'uplink' or 'downlink'.
    Uses Prometheus metrics: oai_gnb_mac_tx_bytes or oai_gnb_mac_rx_bytes
    Returns a dictionary of the form {rnti: value (bits/sec)}
    """
    if direction == "downlink":
        metric = "oai_gnb_mac_tx_bytes"
    elif direction == "uplink":
        metric = "oai_gnb_mac_rx_bytes"
    else:
        log.warning(f"Invalid MAC direction: {direction}")
        return {}

    # query = f'rate({metric}[{TIME_RANGE}]) * 8'  # bytes/sec -> bits/sec
    # log.debug(query)
    # params = {'query': query}
    # results = query_prometheus(params, MONARCH_THANOS_URL)

    # throughput_per_rnti = {}
    # if results:
    #     for result in results:
    #         rnti = result["metric"]["rnti"]
    #         value = float(result["value"][1])
    #         if rnti:
    #             throughput_per_rnti[rnti] = value
    # return throughput_per_rnti

    utc = timezone.utc
    end_time = datetime.now(utc)
    start_time = end_time - timedelta(seconds=int(TIME_RANGE[:-1]))

    end_data = query_prometheus({
        "query": f"{metric}",
        "time": end_time.replace(tzinfo=None).timestamp()
    }, MONARCH_THANOS_URL)

    start_data = query_prometheus({
        "query": f"{metric}",
        "time": start_time.replace(tzinfo=None).timestamp()
    }, MONARCH_THANOS_URL)

    # match RNTIs and compute throughput manually
    throughput_per_rnti = {}

    for result in end_data:
        rnti = result["metric"]["rnti"]
        end_value = float(result["value"][1])
        start_value = next(
            (float(r["value"][1]) for r in start_data if r["metric"]["rnti"] == rnti), None
        )
        if start_value is not None:
            delta_bytes = end_value - start_value
            bits_per_sec = (delta_bytes * 8) / int(TIME_RANGE[:-1])  # seconds
            throughput_per_rnti[rnti] = bits_per_sec
    return throughput_per_rnti 
   
def get_number_ues():
    rntis = set()
    metric = "oai_gnb_mac_tx_bytes"
    
    query = f'rate({metric}[{TIME_RANGE}])'
    results = query_prometheus({'query': query}, MONARCH_THANOS_URL)

    if not results:
        log.warning("No rate results from oai_gnb_mac_tx_bytes for number_ues")
        return 0

    for result in results:
        rnti = result["metric"].get("rnti")
        value = float(result["value"][1])
        log.debug(f"RNTI: {rnti}, rate: {value}")
        if rnti and value > 0:
            rntis.add(rnti)

    count = len(rntis)
    log.info(f"Found {count} active RNTIs (non-zero tx rate) for number_ues")
    return count

def get_saturation_percentage():
    """
    Compute gNB PRB saturation only for UEs with active traffic:
    (sum of mac_nprb for active UEs) / (total PRBs from L1 stats) * 100
    """
    active_rntis = set()
    tx_bytes_query = f'rate(oai_gnb_mac_tx_bytes[{TIME_RANGE}])'
    tx_results = query_prometheus({"query": tx_bytes_query}, MONARCH_THANOS_URL)

    
    if tx_results:
        for result in tx_results:
            rnti = result["metric"].get("rnti")
            value = float(result["value"][1])
            if rnti and value > 0:
                active_rntis.add(rnti)
    else:
        log.warning("No active RNTIs found from tx_bytes rate")

    log.info(f"Found {len(active_rntis)} active RNTIs (non-zero tx rate) for number_ues")
    mac_nprb_query = "oai_gnb_mac_nprb"
    nprb_results = query_prometheus({"query": mac_nprb_query}, MONARCH_THANOS_URL)

    total_nprb = 0.0
    if nprb_results:
        for result in nprb_results:
            try:
                rnti = result["metric"]["rnti"]
                if rnti in active_rntis:
                    val = float(result["value"][1])
                    total_nprb += val
                    log.debug(f"NPRB for active RNTI {rnti}: {val}")
            except (KeyError, ValueError) as e:
                log.warning(f"Failed to parse NPRB result: {e}")
    else:
        log.warning("No results for oai_gnb_mac_nprb")

    l1_result = query_prometheus({"query": "oai_gnb_l1_total_prbs"}, MONARCH_THANOS_URL)
    if not l1_result:
        log.warning("No results for oai_gnb_l1_total_prbs")
        return

    try:
        total_prbs = float(l1_result[0]["value"][1])
        log.debug(f"Total PRBs from L1: {total_prbs}")
    except (IndexError, KeyError, ValueError) as e:
        log.warning(f"Error parsing total PRBs: {e}")
        return

    if total_prbs == 0:
        log.warning("Total PRBs is zero, cannot divide!")
        return

    saturation_percentage = (total_nprb / total_prbs) * 100
    log.info(f"Computed Saturation = {saturation_percentage:.2f}% (Active NPRBs={total_nprb}, Total PRBs={total_prbs})")
    return saturation_percentage

def get_saturation_percentage_per_rnti():
    """
    Compute gNB PRB saturation only for UEs with active traffic:
    (sum of mac_nprb for active UEs) / (total PRBs from L1 stats) * 100
    Returns a dictionary of the form {rnti: value (percentage)}
    """
    active_rntis = set()
    tx_bytes_query = f'rate(oai_gnb_mac_tx_bytes[{TIME_RANGE}])'
    tx_results = query_prometheus({"query": tx_bytes_query}, MONARCH_THANOS_URL)

    
    if tx_results:
        for result in tx_results:
            rnti = result["metric"].get("rnti")
            value = float(result["value"][1])
            if rnti and value > 0:
                active_rntis.add(rnti)
    else:
        log.warning("No active RNTIs found from tx_bytes rate")

    log.info(f"Found {len(active_rntis)} active RNTIs (non-zero tx rate) for number_ues")

    l1_result = query_prometheus({"query": "oai_gnb_l1_total_prbs"}, MONARCH_THANOS_URL)
    if not l1_result:
        log.warning("No results for oai_gnb_l1_total_prbs")
        return

    try:
        total_prbs = float(l1_result[0]["value"][1])
        log.debug(f"Total PRBs from L1: {total_prbs}")
    except (IndexError, KeyError, ValueError) as e:
        log.warning(f"Error parsing total PRBs: {e}")
        return

    if total_prbs == 0:
        log.warning("Total PRBs is zero, cannot divide!")
        return

    mac_nprb_query = "oai_gnb_mac_nprb"
    nprb_results = query_prometheus({"query": mac_nprb_query}, MONARCH_THANOS_URL)

    nprbs = {}
    total_nprb = 0.0
    if nprb_results:
        for result in nprb_results:
            try:
                rnti = result["metric"]["rnti"]
                if rnti in active_rntis:
                    val = float(result["value"][1])
                    total_nprb += val
                    nprbs[rnti] = val
                    log.debug(f"NPRB for active RNTI {rnti}: {val}")
            except (KeyError, ValueError) as e:
                log.warning(f"Failed to parse NPRB result: {e}")
    else:
        log.warning("No results for oai_gnb_mac_nprb")

    saturation_percentage_per_rnti = {}
    for rnti, nprb in nprbs.items():
        saturation_percentage_per_rnti[rnti] = (nprb / total_nprb) * 100
        log.info(f"Computed Saturation = {saturation_percentage_per_rnti[rnti]:.2f}%")

    return saturation_percentage_per_rnti

def get_active_snssais():
    """
    Return a list of active SNSSAIs from the SMF.
    """
    time_range = TIME_RANGE
    query = f'sum by (snssai) (rate(fivegs_smffunction_sm_seid_session[{time_range}]))'
    log.debug(query)
    params = {'query': query}
    results = query_prometheus(params, MONARCH_THANOS_URL)
    active_snssais = [result["metric"]["snssai"] for result in results]
    return active_snssais

def main():
    log.info("Starting Prometheus server on port {}".format(EXPORTER_PORT))

    if not MONARCH_THANOS_URL:
        log.error("MONARCH_THANOS_URL is not set")
        return 

    log.info(f"Monarch Thanos URL: {MONARCH_THANOS_URL}")
    log.info(f"Time range: {TIME_RANGE}")
    log.info(f"Update period: {UPDATE_PERIOD}")
    prom.start_http_server(EXPORTER_PORT)

    while True:
        try:
            run_kpi_computation()
        except Exception as e:
            log.error(f"Failing to run KPI computation: {e}")
        time.sleep(UPDATE_PERIOD)

def export_to_prometheus(snssai, seid, direction, value):
    value_mbits = round(value / 10 ** 6, 6)
    log.info(f"SNSSAI={snssai} | SEID={seid} | DIR={direction:8s} | RATE (Mbps)={value_mbits}")
    SLICE_THROUGHPUT.labels(snssai=snssai, seid=seid, direction=direction).set(value)

def export_mac_throughput_to_prometheus(rnti, direction, value):
    value_mbits = round(value / 10 ** 6, 6)
    log.info(f"RNTI={rnti} | DIR={direction} | RATE (Mbps)={value_mbits}")
    MAC_THROUGHPUT.labels(rnti=rnti, direction=direction).set(value)

def export_number_ues_to_prometheus(value):
    log.info(f"VALUE ={value}")
    NUMBER_UES.set(value)

# def export_saturation_percentage_to_prometheus(value):
#     log.info(f"VALUE ={value}")
#     SATURATION_PERCENTAGE.set(value)

def export_saturation_percentage_to_prometheus(rnti, value):
    log.info(f"RNTI={rnti} | VALUE ={value}")
    SATURATION_PERCENTAGE.labels(rnti=rnti).set(value)

def run_kpi_computation():
    directions = ["uplink", "downlink"]
    active_snssais = get_active_snssais()
    if not active_snssais:
        log.warning("No active SNSSAIs found")
        return
    
    log.debug(f"Active SNSSAIs: {active_snssais}")
    for snssai in active_snssais:
        for direction in directions:
            throughput_per_seid = get_slice_throughput_per_seid_and_direction(snssai, direction)
            for seid, value in throughput_per_seid.items():
                export_to_prometheus(snssai, seid, direction, value)

    for direction in directions:
        mac_throughput = get_mac_throughput_per_rnti_and_direction(direction)
        for rnti, value in mac_throughput.items():
            export_mac_throughput_to_prometheus(rnti, direction, value)
    
    number_ues = get_number_ues()
    export_number_ues_to_prometheus(number_ues)

    # saturation_percentage = get_saturation_percentage()
    # export_saturation_percentage_to_prometheus(saturation_percentage)

    saturation_percentage = get_saturation_percentage_per_rnti()
    for rnti, value in saturation_percentage.items():
        export_saturation_percentage_to_prometheus(rnti, value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='KPI calculator.')
    parser.add_argument('--log', default='info', help='Log verbosity level. Default is "info". Options are "debug", "info", "warning", "error", "critical".')

    args = parser.parse_args()

    # Convert log level from string to logging level
    log_level = getattr(logging, args.log.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(f'Invalid log level: {args.log}')
    
    # setup logger for console output
    log = logging.getLogger(__name__)
    log.setLevel(log_level)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    log.addHandler(console_handler)
        
    main()

    
    


