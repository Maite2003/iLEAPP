__artifacts_v2__ = {
    "get_biomeInfocus": {
        "name": "Biome - In Focus",
        "description": "Parses InFocus Events from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2025-03-05",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/biome/streams/restricted/App.InFocus/local/*'),
        "output_types": "standard"
    }
}


import os
from datetime import timezone
import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv

@artifact_processor
def get_biomeInfocus(context):

    typess = {'10': {'name': '', 'type': 'str'}, '2': {'name': '', 'type': 'int'}, '3': {'name': '', 'type': 'int'},
              '4': {'name': '', 'type': 'double'}, '6': {'name': '', 'type': 'str'}, '9': {'name': '', 'type': 'str'}}

    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
        else:
            continue

        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                protostuff, types = blackboxprotobuf.decode_message(record.data, typess)

                bundleid = (protostuff['6'])
                timestart = (webkit_timestampsconv(protostuff['4']))
                foreground = ('Foreground' if protostuff['3'] == 1 else 'Background')

                data_list.append((ts, timestart, record.state.name, bundleid, foreground, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, filename, record.data_start_offset))

    data_headers = (('Timestamp', 'datetime'), 'Bundle ID', 'Action', 'Filename', 'Offset')

    return data_headers, data_list, ''

