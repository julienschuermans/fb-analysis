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
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_weigths = []
    node_text = []

    # print(next(G.adjacency()))

    for node, adjacencies in enumerate(G.adjacency()):

        sum_of_edge_weights = int(sum([y['weight']
                                       for y in adjacencies[1].values() if not np.isnan(y['weight'])]))
        node_weigths.append(sum_of_edge_weights)
        node_text.append(f'{G.nodes[node].get("name")}\n \
                         #messages: {sum_of_edge_weights}')

    node_trace.marker.color = node_weigths
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    )

    graph = [
        html.H4('Network Interactions'),
        dcc.Graph(
            id='network graph',
            figure=fig,
        ),
    ]
    return graph
