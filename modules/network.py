import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import numpy as np


def build_graph(matrix, names):
    G = nx.from_numpy_matrix(matrix)
    # nx.relabel_nodes(G, {i: names[i] for i in G.nodes()})
    pos = nx.layout.spring_layout(G)
    for node in G.nodes:
        G.nodes[node]['name'] = names[node]
        G.nodes[node]['pos'] = list(pos[node])
    return G


def plot_graph(G):
    edge_x = []
    edge_y = []
    edge_weights = []

    matrix = nx.convert.to_dict_of_dicts(G)
    for edge in G.edges():
        if edge[0] != edge[1] and not np.isnan(matrix[edge[0]][edge[1]]['weight']):
            x0, y0 = G.nodes[edge[0]]['pos']
            x1, y1 = G.nodes[edge[1]]['pos']
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

            edge_weights.append(int(matrix[edge[0]][edge[1]]['weight']))

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(
            width=0.5,
            color='#888'
        ),
        hoverinfo='none',
        mode='lines')

    edge_trace.marker.line.color = edge_weights

    node_x = []
    node_y = []
    node_weights = []
    node_text = []

    for node, adjacencies in enumerate(G.adjacency()):
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

        sum_of_edge_weights = int(sum([y['weight']
                                       for y in adjacencies[1].values() if not np.isnan(y['weight'])]))
        node_weights.append(sum_of_edge_weights)
        node_text.append(f'{G.nodes[node].get("name")}\n \
                         #messages: {sum_of_edge_weights}')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=node_weights,
            cmax=np.percentile(node_weights, 95),
            cmin=10,
            size=10,
            colorbar=dict(
                thickness=15,
                title='# Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    )

    return fig
