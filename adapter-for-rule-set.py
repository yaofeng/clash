#%pip install pyyaml

import yaml
import os
import re
import requests

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
config_directory = os.path.join(current_directory, "configs")
src_config_file = "config_src.yaml"
target_config_file = "config.yaml"

with open(os.path.join(config_directory, src_config_file), "r", encoding="utf-8") as file:
    src_config_dict = yaml.safe_load(file)

with open(os.path.join(config_directory, src_config_file), "r", encoding="utf-8") as file:
    dest_config_dict = yaml.safe_load(file)
    dest_config_dict["rules"] = []
    if dest_config_dict.get("rule-providers"):
        del dest_config_dict["rule-providers"]

for r in src_config_dict["rules"]:
    if not r.startswith("RULE-SET,"):
        dest_config_dict["rules"].append(r)
        continue
    _, rp_name, group_name = r.split(",")
    rp_config = src_config_dict['rule-providers'][rp_name]
    rp_url = rp_config["url"]
    rp_behavior = rp_config["behavior"]
    print(f"Loading rule-set '{rp_name}' ...     ", end="")
    rp_content = requests.get(rp_url).text
    rp_yaml = yaml.safe_load(rp_content)
    print(f"[OK] {len(rp_yaml['payload'])} rules loaded.")
    for item in rp_yaml["payload"]:
        if rp_behavior == "ipcidr":
            item = f"IP-CIDR,{item},{group_name}"
        elif rp_behavior == "domain":
            item = f"DOMAIN,{item},{group_name}"
        elif rp_behavior == "classical":
            if item.endswith(",no-resolve"):
                item = f"{item.replace(',no-resolve', '')},{group_name},no-resolve"
            else:
                item = f"{item},{group_name}"
        dest_config_dict["rules"].append(item)

with open(os.path.join(config_directory, target_config_file), "w", encoding="utf-8") as file:
    yaml.safe_dump(dest_config_dict, file, allow_unicode=True)