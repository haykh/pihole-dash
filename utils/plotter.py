from typing import List
import itertools

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import dash

from .dataobj import QueryData
from .defs import *

layout_plotly = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis={
        'zerolinecolor': 'rgba(255,255,255,0.45)',
        'gridcolor': 'rgba(255,255,255,0.25)',
    },
    yaxis={
        'zerolinecolor': 'rgba(255,255,255,0.45)',
        'gridcolor': 'rgba(255,255,255,0.25)',
    },
    uirevision='constant',
    modebar= {
        'orientation': 'v'
    }
)
external_stylesheets = [
    {
        'href': 'https://fonts.googleapis.com',
        'rel': 'preconnect',
    },
    {
        'href': 'https://fonts.gstatic.com',
        'rel': 'preconnect',
        'crossorigin': 'anonymous'
    },
    {
        'href': 'https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,800;1,400&display=swap',
        'rel': 'stylesheet'
    }
]


class Plotter:
    def __init__(self, fname: str) -> None:
        self.pihole_data = None
        self.loadData(fname)

        self.status_checklist = dash.html.Div([
            dash.dcc.Checklist(
                self.pihole_data.allStatuses(),
                self.pihole_data.allStatuses(),
                inline=True, className="checklist", id="status-check"),
            dash.html.Span([
                "Query status",
            ]),
        ])

        self.type_checklist = dash.html.Div([
            dash.dcc.Checklist(
                self.pihole_data.allTypes(),
                self.pihole_data.allTypes(),
                inline=True, className="checklist", id="type-check"),
            dash.html.Span([
                "Query types",
            ]),
        ], id="type-checklist")

        self.client_dropdown = dash.html.Div([
            dash.html.Span([
                "Clients",
            ]),
            dash.dcc.Dropdown(
                self.pihole_data.allClients(),
                self.pihole_data.allClients(),
                multi=True, searchable=False,
                placeholder="Select clients",
                id="client-select"
            )
        ], className="multi-dropdown")
        self.graph = dash.dcc.Graph(id='graph', config={'displaylogo': False})

    def __del__(self) -> None:
        del self.pihole_data
        del self.app
        del self.graph
        del self.client_dropdown
        del self.status_checklist
        del self.type_checklist

    def loadData(self, fname: str) -> None:
        del self.pihole_data
        self.pihole_data = QueryData(fname)

    def deploy(self, debug: bool = False, port: int = 8050) -> None:
        self.app = dash.Dash(
            __name__, external_stylesheets=external_stylesheets)
        self.app.layout = dash.html.Div([
            dash.html.Div([
                self.status_checklist,
                self.type_checklist
            ], className="toolbar"),
            self.graph,
            dash.html.Div([
                self.client_dropdown,
            ], className="toolbar")
        ])

        @self.app.callback(
            dash.Output('graph', 'figure'),
            dash.Input('status-check', 'value'),
            dash.Input('type-check', 'value'),
            dash.Input('client-select', 'value')
        )
        def update_graph(status_value: List[str], type_value: List[str], clients: List[str]) -> go.Figure:
            statuses = list(
                itertools.chain(*[status_lookup[status_help[v]]
                                for v in status_value])
            )
            types = [query_lookup_r[t] for t in type_value]
            self.pihole_data.filter(clients, statuses, types)
            labels = dict(x="date", y="# of queries")
            fig = px.bar(
                x=self.pihole_data.agg[0], y=self.pihole_data.agg[1], labels=labels)
            fig.update_layout(layout_plotly)
            return fig
        pio.templates.default = 'plotly_dark'
        self.app.run_server(debug=debug, port=port)
