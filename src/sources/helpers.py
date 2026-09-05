from datetime import datetime,timezone
import hashlib

def compute_job_id(url: str, source: str) -> str:
    return hashlib.sha256(f"{url}{source}".encode()).hexdigest()

def unix_timestamp_to_iso(timestamp):
    return datetime.fromtimestamp(timestamp, tz = timezone.utc).isoformat()

def find_node_by_type(resolved_graph, node_type):
    for value in resolved_graph.values():
        if value["@type"] == node_type:
            return value
    return None

def resolve_jsonld_graph(graph):
    return {node["@id"] : node for node in graph}