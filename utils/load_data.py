import networkx as nx
import numpy as np
import pandas as pd
from pyprojroot import here


root = here()
datasets = root / "resources/datasets"


def load_seventh_grader_network():
    # read edge list
    df = pd.read_csv(
        datasets / "moreno_seventh/out.moreno_seventh_seventh",
        skiprows=2,
        header=None,
        sep=" "
    )
    df.columns = ["student1", "student2", "count"]

    # read the node metadata
    meta = pd.read_csv(
        datasets / "moreno_seventh/ent.moreno_seventh_seventh.student.gender",
        header=None
    )
    meta.index += 1
    meta.columns = ["gender"]

    # construct graph from edge list
    G = nx.DiGraph()
    for row in df.iterrows():
        G.add_edge(row[1]["student1"], row[1]["student2"], count=row[1]["count"])
    for n in G.nodes():
        G.nodes[n]["gender"] = meta.loc[n]["gender"]
    
    return G

def load_uber_traffic_network(node_dict: dict, edge_dict: dict):
    data = pd.read_csv(
        datasets / "uber/san_francisco-censustracts-2017-4-All-MonthlyAggregate.csv",
        header=0, #0
        sep=","
    )
    json_data = pd.read_json(datasets / "uber/san_francisco_censustracts.json")

    G = nx.Graph()
    # node_dict = {}
    
    # get node attribute and add node to graph
    for node_info in json_data["features"]:
        node_id = int(node_info["properties"]["MOVEMENT_ID"])
        if node_id in node_dict:
            print("wtf")
        else:
            dis_name = node_info["properties"]["DISPLAY_NAME"]
            location = np.mean(np.array(node_info["geometry"]["coordinates"][0][0]), axis=0)
            node_dict[node_id] = {"DISPLAY_NAME": dis_name, "Location": location}
            G.add_node(node_id, name=dis_name, Location=location)
    
    # get edges and avg of multi-edge
    data_row = data.shape[0]    # 1651411
    data_col = data.shape[1]    # 7
    # edge_dict = {}

    for idx in range(data_row):
        if int(data['month'][idx]) != 12:
            continue
        edge_w = float(data["mean_travel_time"][idx])
        source_id = int(data["sourceid"][idx])
        destin_id = int(data['dstid'][idx])
        if (source_id, destin_id) in edge_dict:
            edge_dict[(source_id, destin_id)][0] += edge_w
            edge_dict[(source_id, destin_id)][1] += 1
        elif (destin_id, source_id) in edge_dict:
            edge_dict[(destin_id, source_id)][0] += edge_w
            edge_dict[(destin_id, source_id)][1] += 1
        else:
            edge_dict[(source_id, destin_id)] = [edge_w, 1]

    # add edges to graph
    for key, item in edge_dict.items():
        w = item[0]/item[1]
        G.add_edge(key[0], key[1], weight=w)
    
    return G