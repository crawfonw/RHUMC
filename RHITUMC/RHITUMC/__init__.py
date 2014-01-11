from autoupdate import json_reader as j

VERSION = j.clean_version_json_data(j.get_version_json_from_module('RHITUMC'))