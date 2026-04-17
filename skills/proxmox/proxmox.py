import os, sys, json, requests, argparse
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Node configuration — override via environment variables
NODES_CONFIG = {
    "pve1": {
        "host": os.environ.get("PVE1_HOST", os.environ.get("PVE_HOST", "192.168.1.10")),
        "token": os.environ.get("PVE1_TOKEN", os.environ.get("PVE_TOKEN", ""))
    },
    "pve2": {
        "host": os.environ.get("PVE2_HOST", os.environ.get("PVE_HOST", "192.168.1.11")),
        "token": os.environ.get("PVE2_TOKEN", os.environ.get("PVE_TOKEN", ""))
    }
}

def get_config(node):
    return NODES_CONFIG.get(node, NODES_CONFIG["pve1"])

def get(endpoint, node="pve1"):
    cfg = get_config(node)
    base = f"https://{cfg['host']}:8006/api2/json"
    headers = {"Authorization": f"PVEAPIToken={cfg['token']}"}
    r = requests.get(f"{base}/{endpoint}", headers=headers, verify=False)
    r.raise_for_status()
    return r.json().get("data", {})

def nodes(node="pve1"):
    return get("nodes", node)

def vms(node="pve1"):
    return get(f"nodes/{node}/qemu", node)

def containers(node="pve1"):
    return get(f"nodes/{node}/lxc", node)

def node_status(node="pve1"):
    return get(f"nodes/{node}/status", node)

def vm_status(node, vmid):
    return get(f"nodes/{node}/qemu/{vmid}/status/current", node)

def storage(node="pve1"):
    return get(f"nodes/{node}/storage", node)

if __name__ == "__main__":
    cmd  = sys.argv[1] if len(sys.argv) > 1 else "nodes"
    arg1 = sys.argv[2] if len(sys.argv) > 2 else "pve1"
    arg2 = sys.argv[3] if len(sys.argv) > 3 else None

    if cmd == "nodes":
        print(json.dumps(nodes(arg1), indent=2))
    elif cmd == "vms":
        print(json.dumps(vms(arg1), indent=2))
    elif cmd == "containers":
        print(json.dumps(containers(arg1), indent=2))
    elif cmd == "status":
        print(json.dumps(node_status(arg1), indent=2))
    elif cmd == "vm":
        print(json.dumps(vm_status(arg1, arg2), indent=2))
    elif cmd == "storage":
        print(json.dumps(storage(arg1), indent=2))
    else:
        print("Usage: proxmox.py [nodes|vms|containers|status|vm|storage] [pve1|pve2] [vmid]")
