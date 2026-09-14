# 🕸️ Macro-Topological Social Network Analysis on X (Twitter): Degree Distributions, Centrality Metrics & Gephi Modularity

## 📖 Overview & Network Science Significance
Conversational interactions across digital microblogging platforms such as **X** (formerly Twitter) form complex, self-organizing scale-free networks. On these platforms, information diffusion, viral propagation, and social polarization are dictated by underlying graph topologies rather than raw tweet volume alone. Understanding how narratives propagate requires analyzing graph mathematical structures: identifying central information brokers, mapping structural echo chambers, and quantifying degree power-law dynamics.

This project performs an extensive **Graph-Theoretic and Social Network Analysis (SNA)** on a large-scale Twitter interaction network using the **Gephi Graph Exploration Platform**. The study rigorously evaluates multi-tier network topologies, including power-law degree scaling, PageRank authority scores, shortest-path network diameters, and modularity-based community detection.

---

## 🛠️ Architecture & Graph Analysis Suite
- **Graph Visualization & Metric Computation**: Gephi Open Graph Visualization Platform (`GEPHI/`).
- **Network Data Structures**: Directed edge-lists and weighted interaction matrices (`DATASET/`).
- **Graph Layout Algorithms**: ForceAtlas2 and Yifan Hu multi-level force-directed spatial distribution models.
- **Computed Graph Metrics**:
  - Degree Distributions: Total Degree, In-Degree (authority), Out-Degree (hub broadcasting).
  - Centrality Dimensions: Betweenness Centrality, Closeness Centrality, Harmonic Closeness, Eigenvector Centrality.
  - Global Graph Statistics: Network Diameter, Graph Density, Average Clustering Coefficient, and Louvain/Blondel Modularity.

---

## 🔄 Methodology & Graph-Theoretic Pipeline

```
Raw Social Interaction Records (Replies, Retweets, Mentions)
                           │
                           ▼
  Directed Graph Formulation: G = (V, E, W)
  ├── Nodes (V): Unique User Accounts
  ├── Edges (E): Interaction Vectors
  └── Weights (W): Interaction Frequency Multipliers
                           │
                           ▼
  Gephi Topological Calculation Engine
  ├── Degree Distribution Fitting (Power-Law Verification)
  ├── Centrality Matrix Computations (Betweenness, PageRank)
  └── Louvain Community Partitioning (Modularity Optimization)
                           │
                           ▼
  Visual Spatial Layouts (ForceAtlas2 & Community Color Mapping)
```

---

## 📊 Key Topological Metrics & Structural Findings

| Graph Metric | Mathematical Formulation / Role | Empirical Observation |
|--------------|--------------------------------|------------------------|
| **Power-Law Degree Distribution** | $P(k) \sim k^{-\gamma}$ (Scale-Free Topology) | Heavy-tailed distribution; <5% of nodes capture >60% of total in-degree |
| **PageRank Authority** | Random walk stationary probability distribution | Isolates authoritative primary sources and verified news broadcasters |
| **Betweenness Centrality** | $g(v) = \sum_{s \ne v \ne t} \frac{\sigma_{st}(v)}{\sigma_{st}}$ | Pinpoints bridge nodes connecting politically polarized sub-networks |
| **Modularity ($Q$)** | Community division optimization (Blondel et al.) | High modularity score ($Q > 0.6$), proving distinct community echo chambers |

### Structural Network Insights:
- **Scale-Free Network Dynamics**: In-degree and out-degree plots exhibit classic power-law decay, confirming that information diffusion is governed by a small core of hyper-connected influencer hubs.
- **Echo-Chamber Segmentation**: Modularity clustering grouped discourse participants into tightly knit clusters with dense intra-group links and minimal cross-group dialogue, reflecting strong ideological polarization.
- **Broker Vulnerability**: High betweenness accounts represent critical single points of failure; disrupting or removing these bridge nodes fractures cross-network communication flow.

---

## 🚀 How to Explore & Reproduce

### 1. Requirements
Download and install the [Gephi Graph Visualization Platform](https://gephi.org/) (Windows/macOS/Linux).

### 2. Inspect Metric Distributions
Pre-calculated distribution graphs, modularity reports, and centrality plots are cataloged in:
```bash
GEPHI/average_degree/
├── degree-distribution.png
├── indegree-distribution.png
├── outdegree-distribution.png
├── page_rank/pagerank-distribution.png
└── modularity/communities-size-distribution.png
```

### 3. Load Project in Gephi
Launch Gephi, click **Open Project**, and import the network dataset from the `DATASET/` directory to run live ForceAtlas2 spatial layouts and manipulate dynamic graph filters.

---

## 🖼️ Community Size Distribution & Modularity
![Project Preview](./preview.png)
