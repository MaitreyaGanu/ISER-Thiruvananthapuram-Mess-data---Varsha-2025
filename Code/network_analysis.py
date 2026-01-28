# =========================
# Mess–Vendor Network Analysis (Varsha 2025)
# =========================

import mysql.connector
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms.community import greedy_modularity_communities
from networkx.algorithms.community.quality import modularity

# -------------------------
# 1. DATABASE CONNECTION
# -------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="...........",
    database="mess_dw"
)

query = """
SELECT
    v.vendor_name,
    m.mess_unit_name,
    SUM(f.amount) AS total_amount
FROM fact_expense f
JOIN dim_vendor v ON f.vendor_id = v.vendor_id
JOIN dim_mess_unit m ON f.mess_unit_id = m.mess_unit_id
GROUP BY v.vendor_name, m.mess_unit_name
"""

df = pd.read_sql(query, conn)
conn.close()

# -------------------------
# 2. BUILD WEIGHTED GRAPH
# -------------------------
G = nx.Graph()

for _, row in df.iterrows():
    vendor = row["vendor_name"]
    mess = row["mess_unit_name"]
    weight = row["total_amount"]

    # Add nodes with type
    G.add_node(vendor, node_type="vendor")
    G.add_node(mess, node_type="mess")

    # Add weighted edge
    G.add_edge(vendor, mess, weight=weight)

print(f"\nTotal nodes: {G.number_of_nodes()}")
print(f"Total edges: {G.number_of_edges()}")

# -------------------------
# 3. CENTRALITY METRICS
# -------------------------
degree_centrality = nx.degree_centrality(G)

weighted_degree = {
    node: sum(data["weight"] for _, _, data in G.edges(node, data=True))
    for node in G.nodes()
}

centrality_df = pd.DataFrame({
    "node": list(G.nodes()),
    "degree_centrality": [degree_centrality[n] for n in G.nodes()],
    "weighted_degree": [weighted_degree[n] for n in G.nodes()]
}).sort_values(by="weighted_degree", ascending=False)

print("\nTop high-dependency nodes:")
print(centrality_df.head(10))

# -------------------------
# 4. COMMUNITY DETECTION
# -------------------------
communities = list(greedy_modularity_communities(G, weight="weight"))

modularity_score = modularity(G, communities, weight="weight")

print(f"\nModularity score: {modularity_score:.3f}")
print(f"Number of communities: {len(communities)}")

for i, c in enumerate(communities):
    print(f"Community {i}: {len(c)} nodes")

# -------------------------
# 5. COMMUNITY COLOR MAP
# -------------------------
community_map = {}
for i, community in enumerate(communities):
    for node in community:
        community_map[node] = i

colors = [community_map[n] for n in G.nodes()]

# -------------------------
# 6. NETWORK VISUALIZATION
# -------------------------
plt.figure(figsize=(14, 10))
pos = nx.spring_layout(G, seed=42, k=0.25)

nx.draw_networkx_edges(
    G, pos,
    alpha=0.3,
    width=0.8
)

nodes = nx.draw_networkx_nodes(
    G, pos,
    node_color=colors,
    cmap=plt.cm.tab10,
    node_size=140,
    alpha=0.9
)

plt.title(
    f"Community Structure of Mess–Vendor Network (Varsha 2025)\n"
    f"Modularity Score = {modularity_score:.3f}",
    fontsize=14
)

# -------------------------
# 7. COMMUNITY LEGEND
# -------------------------
handles = []
for i in range(len(communities)):
    handles.append(
        plt.Line2D(
            [0], [0],
            marker='o',
            linestyle='',
            color=plt.cm.tab10(i),
            label=f"Community {i}"
        )
    )

plt.legend(
    handles=handles,
    title="Detected Communities",
    loc="best",
    fontsize=10
)

plt.axis("off")
plt.tight_layout()
plt.show()

# -------------------------
# 8. TOP FINANCIAL DEPENDENCY BARPLOT
# -------------------------
top_nodes = centrality_df.head(10)

plt.figure(figsize=(8, 5))
plt.barh(
    top_nodes["node"],
    top_nodes["weighted_degree"]
)
plt.xlabel("Total Expense (₹)")
plt.title("Top Financial Dependency Nodes (Varsha 2025)")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

# -------------------------
# 9. INTERPRETATION SUMMARY
# -------------------------
print("\nINTERPRETATION:")
print("- High modularity → strong separation between mess ecosystems")
print("- Mess units act as financial hubs")
print("- Vendors with high weighted degree are risk concentration points")
print("- UNKNOWN / cash-type nodes require audit attention")
print("- Network structure supports targeted procurement optimization")
# Interpret detected communities

community_summary = []

for i, community in enumerate(communities):
    mess_counts = {"CDH-1": 0, "CDH-2": 0, "CAFE": 0, "UNKNOWN": 0}

    for node in community:
        if node in mess_counts:
            mess_counts[node] += 1

    dominant = max(mess_counts, key=mess_counts.get)

    community_summary.append({
        "community_id": i,
        "size": len(community),
        "dominant_mess": dominant,
        "composition": mess_counts
    })

community_df = pd.DataFrame(community_summary)
print(community_df)
