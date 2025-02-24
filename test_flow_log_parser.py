import unittest
from unittest.mock import patch, mock_open
from collections import defaultdict
from parse_flow_logs import create_lookup_table, load_protocols, parse_flow_logs, write_output, LOOKUP, PROTOCOLS

class TestFlowLogParser(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='dstport,protocol,tag\n80,tcp,web\n443,tcp,secure_web\n')
    def test_create_lookup_table(self, mock_file):
        create_lookup_table('lookup.csv')
        self.assertEqual(LOOKUP, {(80, 'tcp'): 'web', (443, 'tcp'): 'secure_web'})
        mock_file.assert_called_with('lookup.csv', 'r')

    @patch('builtins.open', new_callable=mock_open, read_data='number,name\n6,tcp\n17,udp\n')
    def test_load_protocols(self, mock_file):
        load_protocols('protocols.csv')
        self.assertEqual(PROTOCOLS, {6: 'tcp', 17: 'udp'})
        mock_file.assert_called_with('protocols.csv', 'r')

    @patch('builtins.open', new_callable=mock_open, read_data='2 6 123 456 789 101 80 6 some_extra_data more_data 10 20 30 40\n')
    @patch('parse_flow_logs.PROTOCOLS', {6: 'tcp'})
    @patch('parse_flow_logs.LOOKUP', {(80, 'tcp'): 'web'})
    def test_parse_flow_logs(self, mock_file):
        tag_counts, port_protocol_counts = parse_flow_logs('flowlogs.txt')

        self.assertEqual(tag_counts, {'web': 1})
        self.assertEqual(port_protocol_counts, {(80, 'tcp'): 1})
        mock_file.assert_called_with('flowlogs.txt', 'r')

    @patch('builtins.open', new_callable=mock_open)
    def test_write_output(self, mock_file):
        tag_counts = {'web': 1}
        port_protocol_counts = {(80, 'tcp'): 1}

        write_output(tag_counts, port_protocol_counts)

        mock_file.assert_any_call('parse-flow-logs-master/tc_output.txt', 'w')
        mock_file.assert_any_call('parse-flow-logs-master/ppc_output.txt', 'w')

if __name__ == '__main__':
    unittest.main()
