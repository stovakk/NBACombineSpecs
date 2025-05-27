import pandas as pd
from dash import Dash, html, dcc, Input, Output, State
from utils.data_downloader import download_draft_combine_anthro_data, download_draft_combine_drill_data
from utils.data_cleaner import clean_and_merge
from utils.player_loader import load_custom_players
from components.distance_calculator import calculate_player_distances
import plotly.express as px

# Load and clean data
anthro_data_all, drill_data_all = [], []
for year in range(2000, 2025):
    season = f"{year}-{str(year+1)[2:]}"
    anthro = download_draft_combine_anthro_data(season=season)
    drill = download_draft_combine_drill_data(season=season)
    anthro['Season'], drill['Season'] = season, season
    anthro_data_all.append(anthro)
    drill_data_all.append(drill)

merged_df = clean_and_merge(anthro_data_all, drill_data_all)
utah_players = load_custom_players()

app = Dash(__name__)

app.layout = html.Div([
    html.H1("NBA Player Comparison Dashboard", style={"textAlign": "center"}),

    html.Div([
        html.Label("Select a Utah Player"),
        dcc.Dropdown(
            id="utah-player-dropdown",
            options=[{"label": name, "value": name} for name in utah_players["Player"]],
            placeholder="Choose a player...",
            style={"width": "50%", "marginBottom": "20px"}
        )
    ]),

    html.Div([
        html.Div([
            html.Label("Height Without Shoes (inches)"),
            dcc.Input(id="height-input", type="number", placeholder="e.g., 80",
                      style={"height": "30px", "width": "100%"})
        ]),
        html.Div([
            html.Label("Wingspan (inches)"),
            dcc.Input(id="wingspan-input", type="number", placeholder="e.g., 85",
                      style={"height": "30px", "width": "100%"})
        ]),
        html.Div([
            html.Label("Standing Reach (inches)"),
            dcc.Input(id="reach-input", type="number", placeholder="e.g., 108",
                      style={"height": "30px", "width": "100%"})
        ]),
        html.Div([
            html.Label("Hand Length (inches)"),
            dcc.Input(id="hand-length-input", type="number", placeholder="e.g., 8.25",
                      style={"height": "30px", "width": "100%"})
        ]),
        html.Div([
            html.Label("Hand Width (inches)"),
            dcc.Input(id="hand-width-input", type="number", placeholder="e.g., 8.75",
                      style={"height": "30px", "width": "100%"})
        ]),
        html.Div([
            html.Button("Find Closest Players", id="submit-button", n_clicks=0,
                        style={
                            "height": "45px",
                            "padding": "0 20px",
                            "fontSize": "16px",
                            "textAlign": "center",
                            "display": "block"
                        })
        ], style={
            "gridColumn": "span 2",
            "display": "flex",
            "justifyContent": "center",
            "marginTop": "20px"
        })
    ], style={
        "maxWidth": "900px",
        "margin": "0 auto",
        "display": "grid",
        "gridTemplateColumns": "1fr 1fr",
        "gap": "20px 190px",
        "marginBottom": "30px"
    }),

    html.Div(id="closest-players-output", style={"marginTop": "20px"}),
    html.Div(id="averaged-metrics-output", style={"marginTop": "20px"}),
])

@app.callback(
    [Output("height-input", "value"),
     Output("wingspan-input", "value"),
     Output("reach-input", "value"),
     Output("hand-length-input", "value"),
     Output("hand-width-input", "value")],
    [Input("utah-player-dropdown", "value")]
)
def populate_inputs(player_name):
    if player_name:
        row = utah_players[utah_players["Player"] == player_name]
        if not row.empty:
            row = row.iloc[0]
            return (
                row["HEIGHT_WO_SHOES"],
                row["WINGSPAN"],
                row["STANDING_REACH"],
                row["HAND_LENGTH"],
                row["HAND_WIDTH"]
            )
    return [None] * 5

@app.callback(
    [Output("closest-players-output", "children"),
     Output("averaged-metrics-output", "children")],
    [Input("submit-button", "n_clicks")],
    [State("utah-player-dropdown", "value"),
     State("height-input", "value"),
     State("wingspan-input", "value"),
     State("reach-input", "value"),
     State("hand-length-input", "value"),
     State("hand-width-input", "value")]
)
def calculate_and_display(n_clicks, player_name, height, wingspan, reach, hand_length, hand_width):
    if n_clicks > 0 and all([height, wingspan, reach, hand_length, hand_width]):
        player_input = {
            'HEIGHT_WO_SHOES': height,
            'WINGSPAN': wingspan,
            'STANDING_REACH': reach,
            'HAND_LENGTH': hand_length,
            'HAND_WIDTH': hand_width
        }

        distances_df = calculate_player_distances(merged_df, player_input)
        top_names = distances_df.head(6)['PLAYER_NAME'].tolist()
        top_df = merged_df[merged_df['PLAYER_NAME'].isin(top_names)].copy()
        top_df = top_df.merge(distances_df[['PLAYER_NAME', 'Distance']], on='PLAYER_NAME', how='left')

        display_df = top_df.drop(columns=['Distance'], errors='ignore').copy()
        clean_cols = [col.replace('_', ' ').title() for col in display_df.columns]
        col_map = dict(zip(display_df.columns, clean_cols))
        display_df = display_df.rename(columns=col_map)
        display_cols = display_df.columns

        table_rows = [html.Tr([html.Th("#")] + [html.Th(col) for col in display_df.columns])]

        # Build "You" or selected player row
        you_row = pd.Series(index=display_df.columns, dtype=object)

        if player_name:
            matched = utah_players[utah_players["Player"] == player_name]
            if not matched.empty:
                row = matched.iloc[0]
                renamed_row = row.rename({col: col.replace('_', ' ').title() for col in row.index})
                for col in display_df.columns:
                    if col in renamed_row:
                        you_row[col] = renamed_row[col]
                you_row["Player Name"] = player_name
            else:
                you_row.update({
                    'Height Wo Shoes': height,
                    'Wingspan': wingspan,
                    'Standing Reach': reach,
                    'Hand Length': hand_length,
                    'Hand Width': hand_width
                })
                you_row["Player Name"] = "You"
        else:
            you_row.update({
                'Height Wo Shoes': height,
                'Wingspan': wingspan,
                'Standing Reach': reach,
                'Hand Length': hand_length,
                'Hand Width': hand_width
            })
            you_row["Player Name"] = "You"

        row_cells = [html.Td("—")] + [
            html.Td(str(you_row[col]) if pd.notna(you_row[col]) else "—") for col in display_df.columns
        ]
        table_rows.append(html.Tr(row_cells))

        table_rows.append(html.Tr([html.Td("—") for _ in range(len(display_df.columns) + 1)]))

        for i, (_, row) in enumerate(display_df.iterrows(), 1):
            row_cells = [html.Td(f"{i}.")] + [html.Td(str(row[col]) if pd.notna(row[col]) else "—") for col in display_df.columns]
            table_rows.append(html.Tr(row_cells))

        player_table = html.Div([
            html.Table(table_rows, className="data-table")
        ], style={
            "overflowX": "auto",
            "maxWidth": "100%",
            "border": "1px solid #ccc",
            "padding": "10px",
            "borderRadius": "10px",
            "backgroundColor": "#f9f9f9"
        })

        exclude_fields = ['Height Wo Shoes', 'Wingspan', 'Standing Reach', 'Hand Length', 'Hand Width', 'Distance']
        avg_df = display_df.drop(columns=exclude_fields, errors="ignore")
        numeric_df = avg_df.select_dtypes(include='number')
        avg_values = numeric_df.mean().round(2)

        averages_section = html.Div([
            html.H3("Similar Player Average Metrics", style={"textAlign": "center", "marginTop": "30px"}),
            html.Div([
                html.Div([
                    html.Div(col, className="metric-label"),
                    html.Div(f"{val}", className="metric-value")
                ], className="metric-box") for col, val in avg_values.items()
            ], className="averages-container")
        ])

        graphs = []
        player_name_col = display_df['Player Name']
        for col in numeric_df.columns:
            y_values = display_df[col]
            sorted_vals = sorted(y_values.dropna())
            y_min = sorted_vals[1] * 0.95 if len(sorted_vals) >= 2 and sorted_vals[0] == 0 else (sorted_vals[0] * 0.95 if sorted_vals else 0)
            y_max = max(sorted_vals) * 1.05 if sorted_vals else 1

            fig = px.bar(x=player_name_col, y=y_values, labels={'x': 'Player Name', 'y': col}, title=col, height=300)
            fig.update_yaxes(range=[y_min, y_max])

            graphs.append(dcc.Graph(figure=fig))

        graph_section = html.Div([
            html.H3("Metric Comparisons Across Closest Players", style={"textAlign": "center", "marginTop": "40px"}),
            html.Div(graphs)
        ])

        return player_table, html.Div([averages_section, graph_section])

    return "", ""

if __name__ == "__main__":
    app.run(debug=True)
