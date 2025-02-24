import csv
import logging
import configparser

from collections import defaultdict
from typing import Dict, Tuple


"""
LOOKUP and PROTOCOLS are global dictionaries that will be populated from the lookup and protocols files.

LOOKUP = {
    (dstport, protocol): tag
}
PROTOCOLS = {
    protocol_number: protocol_name
}
"""

LOOKUP: Dict[Tuple[int, str], str] = {}
PROTOCOLS: Dict[int, str] = {}

# Load configuration
config = configparser.ConfigParser()
config.read('parse-flow-logs-master/config.ini')
files = config['files']

FLOW_LOG_FILE = files['flow_log_file'] if 'flow_log_file' in files else 'flowlogs.txt'
LOOKUP_FILE = files['lookup_file'] if 'lookup_file' in files else 'lookup.csv'

TAG_COUNTS_OUTPUT_FILE = files['tag_counts_output_file'] if 'tag_counts_output_file' in files else 'tag_counts.csv'
PORT_PROTOCOL_COUNTS_OUTPUT_FILE = files['port_protocol_counts_output_file'] if 'port_protocol_counts_output_file' in files else 'port_protocol_counts.csv'

PROTOCOLS_FILE = files['protocols_file'] if 'protocols_file' in files else 'protocols.csv'
MIN_FIELDS_IN_LOG = 14

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')


def load_protocols(protocols_file: str) -> None:
    """
    Read protocols file and populate the PROTOCOLS dictionary.

    Args:
        protocols_file (str): Path to the protocols file
    """
    logging.info(f"Loading protocols from {protocols_file}")
    with open(protocols_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            PROTOCOLS[int(row['number'])] = row['name'].lower()


def create_lookup_table(lookup_file: str) -> None:
    """
    Read lookup table and populate the LOOKUP dictionary.

    Args:
    lookup_file (str): Path to the lookup file.
    """
    logging.info(f"Creating lookup table from {lookup_file}")
    with open(lookup_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (int(row['dstport']), row['protocol'].lower())
            LOOKUP[key] = row['tag']


def parse_flow_logs(flow_log_file: str) -> Tuple[Dict[str, int], Dict[Tuple[int, str], int]]:
    """
    Parse flow logs and return the tag counts and port-protocol counts.

    Args:
        flow_log_file (str): Path to the flow log file.

    Returns:
        Tuple[Dict[str, int], Dict[Tuple[int, str], int]]: A tuple containing
        tag counts and port-protocol counts.
    """
    # Initialize counters
    tag_counts = defaultdict(int)
    port_protocol_counts = defaultdict(int)

    logging.info(f"Parsing flow logs from {flow_log_file}")
    try:
        with open(flow_log_file, 'r') as f:
            for line_number, log_entry in enumerate(f, start=1):
                fields = log_entry.strip().split()
                if len(fields) < MIN_FIELDS_IN_LOG:
                    logging.warning(
                        f"\nInvalid log entry, less than {MIN_FIELDS_IN_LOG} fields at line {line_number}, skipping")
                    continue

                try:
                    dstport = int(fields[6])
                    protocol = PROTOCOLS.get(int(fields[7]), 'unknown')
                except ValueError:
                    logging.warning(
                        f"Invalid port or protocol at line {line_number}, skipping")
                    continue

                key = (dstport, protocol)
                tag = LOOKUP.get(key, 'untagged')

                tag_counts[tag] += 1
                port_protocol_counts[key] += 1

    except FileNotFoundError:
        logging.error(f"Flow log file not found: {flow_log_file}")
        raise

    return tag_counts, port_protocol_counts


def write_output(tag_counts: Dict[str, int], port_protocol_counts: Dict[Tuple[int, str], int]) -> None:
    """
    Write the tag counts and port-protocol counts to output files.

    Args:
        tag_counts (Dict[str, int]): Dictionary of tag counts.
        port_protocol_counts (Dict[Tuple[int, str], int]): Dictionary of port-protocol counts.
    """
    logging.info(
        f"Writing output to the files, {TAG_COUNTS_OUTPUT_FILE} and {PORT_PROTOCOL_COUNTS_OUTPUT_FILE}")

    try:
        with open(TAG_COUNTS_OUTPUT_FILE, 'w') as f:
            f.write("Tag,Count\n")
            for tag, count in tag_counts.items():
                f.write(f"{tag},{count}\n")

        with open(PORT_PROTOCOL_COUNTS_OUTPUT_FILE, 'w') as f:
            f.write("Port,Protocol,Count\n")
            for (port, protocol), count in port_protocol_counts.items():
                f.write(f"{port},{protocol},{count}\n")

    except Exception as e:
        logging.error(f"Error writing tag counts to the file: {e}")
        raise


def main():
    """
    Main function to orchestrate the flow log parsing process.
    """
    try:
        create_lookup_table(LOOKUP_FILE)
        load_protocols(PROTOCOLS_FILE)
        tag_counts, port_protocol_counts = parse_flow_logs(FLOW_LOG_FILE)
        write_output(tag_counts, port_protocol_counts)

    except Exception as e:
        logging.error(f"An error occurred during execution: {e}")
        raise


if __name__ == '__main__':
    main()
