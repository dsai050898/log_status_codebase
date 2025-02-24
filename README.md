Step-by-Step Instructions to Run the Code

## Problem

Write a program that can parse a file containing [flow log data](./flowlogs.txt)
and maps each row to a tag based on a [lookup table](./lookup.csv).

## Assumptions

1. The program only supports default log format (v2) (i.e, flow log file will
   have at least 14 fields in each line). If a line has less than 14 fields, it
   will be skipped.
2. The protocols are populated from the [protocols file](/protocols.csv). It has
   the popular protocols listed in the format of
   `protocol_number,protocol_name`. If a protocol is not found in this CSV file,
   it will be counted as `unknown`.

## Usage

```bash
python3 parse_flow_logs.py
```

The program will read the flow logs from `flowlogs.txt` and the lookup table
from `lookup.csv`. It will write the output to `tc_output.txt` and
`ppc_output.txt`. Alternatively, you can specify the filenames in the
[configuration file `config.ini`](./config.ini).

## Step-by-Step Instructions to Run the Code

### **Step 1: Install Python**
Ensure you have Python installed. You can check by running:

```bash
python3 --version
```

If not installed, download and install Python from [python.org](https://www.python.org/).

### **Step 2: Clone or Download the Project**
If you have a Git repository:

```bash
git clone <repo_url>
cd parse-flow-logs-master
```

Or manually **download and extract** the ZIP file.

### **Step 3: Install Dependencies**
If the project requires external dependencies, install them:

```bash
pip install -r requirements.txt
```

(If no `requirements.txt` is provided, this step may be skipped.)

### **Step 4: Ensure Input Files Exist**
Ensure the required input files exist in the project directory:
- `flowlogs.txt` → Contains the network flow logs.
- `lookup.csv` → Contains destination port, protocol, and tag mappings.
- `protocols.csv` → Contains protocol number-to-name mappings.

### **Step 5: Run the Parser**
Run the script to process the logs:

```bash
python3 flow_logs_codebase.py
```

### **Step 6: Check the Output**
The parsed data will be saved in:
- **`tc_output.txt`** → Tag count results.
- **`ppc_output.txt`** → Port/protocol combination counts.

You can view the output using:

```bash
cat tc_output.txt
cat ppc_output.txt
```

### **Step 7: Run Tests (Optional)**
To verify functionality, run unit tests:

```bash
python3 -m unittest test_parse_flow_logs.py
```

### 🎯 **Troubleshooting**
- **File Not Found Error?** Ensure all input files exist in the same directory.
- **Permission Denied?** Try running with elevated permissions:  
  ```bash
  sudo python3 parse_flow_logs.py  # (Mac/Linux)
  ```
- **Python Not Found?** Use `python` instead of `python3`, depending on your system.

## Testing

You can run the unit tests for the program

```bash
python3 -m unittest test_parse_flow_logs.py
```

## Requirements

The program should generate an output file containing the following:

1. Tag Counts: Count of matches for each tag

   ```
   Tag,Count
   sv_P2,1
   sv_P1,2
   sv_P4,1
   email,3
   Untagged,9
   ```

2. Port/Protocol Combination Counts: Count of matches for each port/protocol
   combination

   ```
   Port,Protocol,Count
   22,tcp,1
   23,tcp,1
   25,tcp,1
   110,tcp,1
   143,tcp,1
   443,tcp,1
   993,tcp,1
   1024,tcp,1
   49158,tcp,1
   80,tcp,1
   ```

## Specifications

- Input file as well as the file containing tag mappings are plain text (ascii)
  files.
- The flow log file size can be up to 10 MB.
- The lookup file can have up to 10000 mappings.
- The tags can map to more than one port, protocol combinations. For e.g. sv_P1
  and sv_P2 in the sample above.
- The matches should be case insensitive.

For anything else that is not clear, please make reasonable assumptions and
document those in the Readme to be sent with your submission.

## Notes

### `flowlogs.txt`

Each line in the log entry follows the format of an AWS VPC Flow Log which
records network traffic information for the VPC in AWS. The fields in the log
entry are separated by spaces.

```log
2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 443 49153 6 25 20000 1620140761 1620140821 ACCEPT OK
```

The fields in the log entry are as follows:

```log
version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status
```

The required fields are :

7. Destination Port (`dstport`) [integer]
8. Protocol (`protocol`) [tcp/udp/icmp]

Reference:
https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html#flow-logs-fields

### `lookup.csv`

The lookup table is used to map the destination port and protocol to a tag. The
`dstport` and `protocol` combination decide what `tag` can be applied.

```csv
dstport,protocol,tag
25,tcp,sv_P1
```

The fields in the lookup table are as follows:

1. Destination Port (`dstport`) [integer]
2. Protocol (`protocol`) [tcp/udp/icmp]
3. Tag (`tag`) [string]

## Stress Testing

I created a [python
script](https://gist.github.com/vchrombie/91885dede7c21b3dee6fa8421f130db0)
which generates random flow logs and lookup tables to test the performance of
the program. The script generates flow logs over filesize of 10 MB and lookup
table with more than 10,000 entries. The flow logs are written to `flowlogs.txt`
and the lookup table is written to `lookup.csv`.

```bash
$ python generate_flow_log_data.py

$ wc -l lookup.csv
   10001 lookup.csv

$ du -sh flowlogs.txt
 10M    flowlogs.txt

$ time python parse_flow_logs.py
INFO - Creating lookup table from lookup.csv
INFO - Loading protocols from protocols.csv
INFO - Parsing flow logs from flowlogs.txt
INFO - Writing output to the files, tc_output.txt and ppc_output.txt
python3 parse_flow_logs.py  0.24s user 0.02s system 92% cpu 0.276 total
```

