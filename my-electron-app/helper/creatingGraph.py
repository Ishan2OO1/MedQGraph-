import sys
import json
import os
import pandas as pd
from neo4j import GraphDatabase
from py2neo import Graph
import networkx as nx
import plotly.graph_objects as go

# Neo4j Connection Credentials
URI = "neo4j+s://5f06d1b4.databases.neo4j.io"  # Change if hosted elsewhere
USERNAME = "neo4j"
PASSWORD = "Nk30WHZPhuWpLUeMRHyuspzr-xjoX7zWw1kcTm8JKlE"

# Function to create nodes in Neo4j
def create_nodes(tx, row):
    print(f"Inserting Node for Patient ID: {row['subject_id']}")  # Debugging
    query = """
    MERGE (p:Patient {subject_id: $subject_id})  
    MERGE (a:Admission {hadm_id: $hadm_id, admission_type: $admission_type})
    MERGE (d:Diagnosis {description: $description})
    MERGE (m:Medication {drug_name: $drug})
    MERGE (t:Test {test_name: $test_name})
    MERGE (s:Strength {prod_strength: $prod_strength})
    MERGE (r:Route {route: $route})
    MERGE (at:AdmissionType {admission_type: $admission_type})
    MERGE (al:Location {admission_location: $admission_location})
    MERGE (tr:TestResult {comments: $comments})
    MERGE (dm:MortalityRisk {drg_mortality: $drg_mortality})
    MERGE (ot:OrderType {order_type: $order_type})
    MERGE (ost:OrderSubType {order_subtype: $order_subtype})
    MERGE (i:Insurance {insurance: $insurance})
    MERGE (ms:MaritalStatus {marital_status: $marital_status})
    MERGE (demo:Demographics {race: $race, gender: $gender, age: $anchor_age})
    """
    tx.run(query, **row)

# Function to create relationships in Neo4j
def create_relationships(tx, row):
    print(f"Creating relationships for Patient ID: {row['subject_id']}")  # Debugging
    query = """
    MATCH (p:Patient {subject_id: $subject_id})
    MATCH (a:Admission {hadm_id: $hadm_id})
    MATCH (d:Diagnosis {description: $description})
    MATCH (m:Medication {drug_name: $drug})
    MATCH (t:Test {test_name: $test_name})
    MATCH (s:Strength {prod_strength: $prod_strength})
    MATCH (r:Route {route: $route})
    MATCH (al:Location {admission_location: $admission_location})
    MATCH (tr:TestResult {comments: $comments})
    MATCH (dm:MortalityRisk {drg_mortality: $drg_mortality})
    MATCH (ot:OrderType {order_type: $order_type})
    MATCH (ost:OrderSubType {order_subtype: $order_subtype})
    MATCH (i:Insurance {insurance: $insurance})
    MATCH (ms:MaritalStatus {marital_status: $marital_status})
    MATCH (demo:Demographics {race: $race, gender: $gender, age: $anchor_age})

    MERGE (p)-[:HAS_ADMISSION]->(a)
    MERGE (p)-[:HAS_CONDITION]->(d)
    MERGE (p)-[:HAS_PRESCRIPTION]->(m)
    MERGE (p)-[:UNDERWENT_TEST]->(t)
    MERGE (p)-[:HAS_INSURANCE]->(i)
    MERGE (p)-[:HAS_MARITAL_STATUS]->(ms)
    MERGE (p)-[:HAS_DEMOGRAPHICS]->(demo)
    MERGE (p)-[:ADMITTED_FROM]->(al)
    MERGE (p)-[:HAS_ADMISSION_TYPE]->(at)
    MERGE (d)-[:TREATED_WITH]->(m)
    MERGE (d)-[:ASSOCIATED_WITH_ROUTE]->(r)
    MERGE (d)-[:REQUIRES_TEST]->(t)
    MERGE (m)-[:HAS_STRENGTH]->(s)
    MERGE (m)-[:HAS_MORTALITY_RISK]->(dm)
    MERGE (m)-[:ORDERED_UNDER]->(ot)
    MERGE (t)-[:HAS_RESULT]->(tr)
    MERGE (ot)-[:HAS_SUBTYPE]->(ost)
    """
    tx.run(query, **row)

def process_csv_and_create_graph(file_path):
    print(f"Processing CSV file: {file_path}")  # Debugging
    if not os.path.exists(file_path):
        raise ValueError(f"File at {file_path} does not exist.")
    
    df = pd.read_csv(file_path)
    print("✅ CSV Loaded Successfully! First few rows:")
    print(df.head())  # Print first few rows for debugging
    
    df = df.fillna("Unknown")  # Replace NaN values with "Unknown"
    df = df.head(50)  # Limit to first 250 rows for testing
    
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    
    with driver.session() as session:
        for _, row in df.iterrows():
            session.execute_write(create_nodes, row)
    
    with driver.session() as session:
        for _, row in df.iterrows():
            session.execute_write(create_relationships, row)
    
    print("✅ Knowledge Graph Successfully Created in Neo4j!")

  

    # 🔹 Connect to Neo4j
    neo4j_uri = "neo4j+s://5f06d1b4.databases.neo4j.io"
    neo4j_user = "neo4j"
    neo4j_password = "Nk30WHZPhuWpLUeMRHyuspzr-xjoX7zWw1kcTm8JKlE"

    graph = Graph(neo4j_uri, auth=(neo4j_user, neo4j_password))

    # 🔹 Expanded Cypher Query to Include More Node Attributes
    query = """
    MATCH (n)-[r]->(m)
    RETURN labels(n) AS from_type, 
        COALESCE(n.subject_id, n.hadm_id, n.description, n.drug_name, n.test_name, 
                    n.prod_strength, n.route, n.insurance, n.marital_status, 
                    n.order_type, n.order_subtype, "Unknown") AS from,
        type(r) AS relation, 
        labels(m) AS to_type, 
        COALESCE(m.subject_id, m.hadm_id, m.description, m.drug_name, m.test_name, 
                    m.prod_strength, m.route, m.insurance, m.marital_status, 
                    m.order_type, m.order_subtype, "Unknown") AS to
    LIMIT 1000
    """
    data = graph.run(query).data()

    # 🔹 Debugging Output
    print("\n--- Nodes and Relationships Retrieved ---")
    for row in data:
        print(f"From: {row['from']} ({row['from_type']}), Relation: {row['relation']}, To: {row['to']} ({row['to_type']})")

    # 🔹 Handle Missing Values
    filtered_data = [row for row in data if row["from"] != "Unknown" and row["to"] != "Unknown"]

    # 🔹 Create NetworkX Graph
    G = nx.DiGraph()

    # ✅ Add all nodes
    node_types = {}
    for row in filtered_data:
        from_node = f"{row['from']} ({row['from_type'][0]})"
        to_node = f"{row['to']} ({row['to_type'][0]})"
        
        # Store node types for tracking
        node_types[from_node] = row['from_type'][0]
        node_types[to_node] = row['to_type'][0]

        G.add_node(from_node)
        G.add_node(to_node)

    # ✅ Add all edges
    for row in filtered_data:
        from_node = f"{row['from']} ({row['from_type'][0]})"
        to_node = f"{row['to']} ({row['to_type'][0]})"
        G.add_edge(from_node, to_node, label=row["relation"])

    # 🔹 Generate 3D positions for nodes
    pos = nx.spring_layout(G, dim=3, seed=42)

    node_x, node_y, node_z, node_labels = [], [], [], []
    for node, (x, y, z) in pos.items():
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        node_labels.append(node)

    # ✅ Edge coordinates
    edge_x, edge_y, edge_z = [], [], []
    for edge in G.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])

    # 🔹 Create Plotly 3D Edge Traces
    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(width=1.5, color="gray"),
        hoverinfo='none',
        mode='lines'
    )

    # 🔹 Create Plotly 3D Node Traces (All Nodes in Blue)
    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        marker=dict(size=6, color="blue", opacity=0.9),
        text=node_labels,
        hoverinfo='text'
    )

    # 🔹 Enable Zoom & Orbit Controls
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="3D Knowledge Graph of MIMIC-IV Data (Neo4j)",
        width=1000, height=800,
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            zaxis=dict(showgrid=False, zeroline=False),
        ),
        dragmode="orbit",  # Allows users to rotate, zoom, and pan
        scene_camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.8, y=1.8, z=1.8)  # Adjust eye position for better initial zoom
        )
    )

    fig.show()

    # 🔹 Display Unique Patient IDs
    patient_ids = {row["from"] for row in filtered_data if "Patient" in row["from_type"]} | \
                {row["to"] for row in filtered_data if "Patient" in row["to_type"]}

    print("\n--- Unique Patient IDs in the Knowledge Graph ---")
    print(sorted(patient_ids))

    # 🔹 Graph Statistics
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()

    print(f"\n--- Knowledge Graph Statistics ---")
    print(f"Total Nodes Created: {num_nodes}")
    print(f"Total Relationships Created: {num_edges}")



def main():
    try:
        json_data = sys.argv[1]  # Read first argument (JSON string)
        data = json.loads(json_data)
        file_path = data.get("file_path", "No file path provided")
        
        print(f"📌 Received file path: {file_path}")  # Debugging

        if not os.path.exists(file_path):
            raise ValueError(f"File at {file_path} does not exist.")
        
        process_csv_and_create_graph(file_path)
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    csv_file_path = "uploads/MIMIC_IV Hospital cleaned-1742103641756.csv"  # <-- Update this path
    print(f"Checking file path: {os.path.abspath(csv_file_path)}")  # Debugging
    process_csv_and_create_graph(csv_file_path)  # ✅ FIXED FUNCTION CALL
