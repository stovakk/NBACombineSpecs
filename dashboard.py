import pandas as pd
from dash import Dash, html, dcc, Input, Output, State
from utils.data_downloader import download_draft_combine_anthro_data, download_draft_combine_drill_data
from utils.data_cleaner import clean_and_merge
from components.distance_calculator import calculate_player_distances
import plotly.express as px


# Download and prepare data
anthro_data_all, drill_data_all = [], []
for year in range(2000, 2025):
    season = f"{year}-{str(year+1)[2:]}"
    anthro = download_draft_combine_anthro_data(season=season)
    drill = download_draft_combine_drill_data(season=season)
    anthro['Season'], drill['Season'] = season, season
    anthro_data_all.append(anthro)
    drill_data_all.append(drill)

merged_df = clean_and_merge(anthro_data_all, drill_data_all)
app = Dash(__name__)

# Define renaming and column exclusion
rename_cols = {
    "PLAYER_NAME": "Player",
    "HEIGHT_WO_SHOES": "Height (in)",
    "WINGSPAN": "Wingspan (in)",
    "STANDING_REACH": "Standing Reach (in)",
    "HAND_LENGTH": "Hand Length (in)",
    "HAND_WIDTH": "Hand Width (in)",
    "MAX_VERTICAL_LEAP": "Max Vert (in)",
    "THREE_QUARTER_SPRINT": "Sprint (sec)",
    "STANDING_VERTICAL_LEAP": "Standing Vert (in)",
}

drop_cols = ["MODIFIED_LANE_AGILITY_TIME", "BENCH_PRESS"]

app.layout = html.Div([
    html.H1("NBA Player Comparison Dashboard", style={"textAlign": "center"}),

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
    [Output("closest-players-output", "children"),
     Output("averaged-metrics-output", "children")],
    [Input("submit-button", "n_clicks")],
    [State("height-input", "value"),
     State("wingspan-input", "value"),
     State("reach-input", "value"),
     State("hand-length-input", "value"),
     State("hand-width-input", "value")]
)
def calculate_and_display(n_clicks, height, wingspan, reach, hand_length, hand_width):
    if n_clicks > 0 and all([height, wingspan, reach, hand_length, hand_width]):
        player_input = {
            'HEIGHT_WO_SHOES': height,
            'WINGSPAN': wingspan,
            'STANDING_REACH': reach,
            'HAND_LENGTH': hand_length,
            'HAND_WIDTH': hand_width
        }

        # Step 1: Calculate distances
        distances_df = calculate_player_distances(merged_df, player_input)
        top_names = distances_df.head(6)['PLAYER_NAME'].tolist()

        # Step 2: Get player rows and attach distance
        top_df = merged_df[merged_df['PLAYER_NAME'].isin(top_names)].copy()
        top_df = top_df.merge(distances_df[['PLAYER_NAME', 'Distance']], on='PLAYER_NAME', how='left')

        # Step 3: Clean column names for display
        display_df = top_df.drop(columns=['Distance'], errors='ignore').copy()

        clean_cols = [col.replace('_', ' ').title() for col in display_df.columns]
        col_map = dict(zip(display_df.columns, clean_cols))
        display_df = display_df.rename(columns=col_map)

        # Step 4: Table — include everything
        table_rows = [html.Tr([html.Th("#")] + [html.Th(col) for col in display_df.columns])]
        for i, (_, row) in enumerate(display_df.iterrows(), 1):
            row_cells = [html.Td(f"{i}.")] + [
                html.Td(str(row[col]) if pd.notna(row[col]) else "—") for col in display_df.columns
            ]
            table_rows.append(html.Tr(row_cells))

        player_table = html.Div([
            html.Div([
                html.Table(table_rows, className="data-table")
            ], style={
                "overflowX": "auto",
                "maxWidth": "100%",
                "border": "1px solid #ccc",
                "padding": "10px",
                "borderRadius": "10px",
                "backgroundColor": "#f9f9f9"
            })
        ])


        # Step 5: Averages — exclude user-input fields
        exclude_fields = ['Height Wo Shoes', 'Wingspan', 'Standing Reach', 'Hand Length', 'Hand Width', 'Distance']
        avg_df = display_df.drop(columns=exclude_fields, errors="ignore")
        numeric_df = avg_df.select_dtypes(include='number')
        avg_values = numeric_df.mean().round(2)

        averages_section = html.Div([
            html.H3("Relevant Player Information", style={"textAlign": "center", "marginTop": "30px"}),
            html.Div([
                html.Div([
                    html.Div(col, className="metric-label"),
                    html.Div(f"{val}", className="metric-value")
                ], className="metric-box") for col, val in avg_values.items()
            ], className="averages-container")
        ])

        # Step 6: Graphs for numeric columns (excluding input fields)
        graphs = []
        player_name_col = display_df['Player Name']
        for col in numeric_df.columns:
            y_values = display_df[col]
            sorted_vals = sorted(y_values.dropna())

            # Smart y-axis scaling
            if len(sorted_vals) >= 2 and sorted_vals[0] == 0:
                y_min = sorted_vals[1] * 0.95
            elif len(sorted_vals) >= 1:
                y_min = sorted_vals[0] * 0.95
            else:
                y_min = 0
            y_max = max(sorted_vals) * 1.05 if sorted_vals else 1

            fig = px.bar(
                x=player_name_col,
                y=y_values,
                labels={'x': 'Player Name', 'y': col},
                title=col,
                height=300
            )
            fig.update_yaxes(range=[y_min, y_max])

            graphs.append(
                html.Div([
                    dcc.Graph(figure=fig)
                ], style={"marginBottom": "40px"})
            )

        graph_section = html.Div([
            html.H3("Metric Comparisons Across Closest Players", style={"textAlign": "center", "marginTop": "40px"}),
            html.Div(graphs)
        ])

        return player_table, html.Div([averages_section, graph_section])

    return "", ""

if __name__ == "__main__":
    app.run(debug=True)
