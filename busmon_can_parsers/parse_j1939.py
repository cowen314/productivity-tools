import pandas as pd
from pathlib import Path
from typing import List
from common_utils.busmonitor_parsing import arb_id_str_to_bytearray, payload_str_to_bytearray


class J1939Frame:
    def __init__(self, source_address: int, dest_address: int, payload: bytearray):
        self.source_address = source_address
        self.dest_address = dest_address
        self.payload = payload


trace_path = Path(
    "C:/Users/christiano/DMC SharePoint/Mercury Marine Test Stand - Documents/DMC Only (Private)/Diagnostic CAN Traces/2021 08 20 Files from Georgi/2021_08_20_2690328_Step1.xlsx")

'''
below is a loop that runs through all frames in the trace looking for DM14 write operations
when it finds a DM14 write, it spits out the pointer value
it then looks for a DM16 carrying the data
after it finds a DM16, it starts looking for DM14 write frames again
'''

trace_df = pd.read_excel(trace_path, sheet_name="Sheet 1")
search_for_dm_write_start = True
for frame_label, frame in trace_df.iterrows():
    arb_id = arb_id_str_to_bytearray(frame["ID"])
    pgn_format = arb_id[1]
    payload = payload_str_to_bytearray(frame["Payload"])
    if search_for_dm_write_start:
        if pgn_format == 0xd9:  # DM14
            if (payload[1] & 0b1110) >> 1 == 2:  # a write operation
                search_for_dm_write_start = False
                # parameter_bytes = payload[2:5]
                parameter_value = payload[2] + (payload[3] << 8) + (payload[4] << 16)
                print(f"- Found DM write frame, pointer was '{parameter_value}'")
    if not search_for_dm_write_start:
        # not searching for a DM exchange, so must be searching for DM16 message
        if pgn_format == 0xd7:  # DM16
            print(f"\t- DM16 found, data written was {frame['Payload']}")
            search_for_dm_write_start = True  # reset so that we look for the next DM14 write
