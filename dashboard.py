import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
from utils.data_downloader import download_draft_combine_anthro_data, download_draft_combine_drill_data
from utils.data_cleaner import clean_and_merge
from components.distance_calculator import calculate_player_distances

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
server = app.server

app.layout = html.Div([
    html.H1("NBA Player Comparison Dashboard", style={"textAlign": "center", "marginBottom": "40px"}),

    html.Div([
        html.Div([
            html.Label("Height Without Shoes"),
            dcc.Input(id="height-input", type="number", placeholder="e.g., 80", style={"width": "100%"})
        ], className="input-field"),

        html.Div([
            html.Label("Wingspan"),
            dcc.Input(id="wingspan-input", type="number", placeholder="e.g., 85", style={"width": "5ch"})
        ], className="input-field"),

        html.Div([
            html.Label("Standing Reach"),
            dcc.Input(id="reach-input", type="number", placeholder="e.g., 108", style={"width": "5ch"})
        ], className="input-field"),

        html.Div([
            html.Label("Hand Length"),
            dcc.Input(id="hand-length-input", type="number", placeholder="e.g., 8.25", style={"width": "5ch"})
        ], className="input-field"),

        html.Div([
            html.Label("Hand Width"),
            dcc.Input(id="hand-width-input", type="number", placeholder="e.g., 8.75", style={"width": "5ch"})
        ], className="input-field"),
    ], className="input-row"),

    html.Div([
        html.Button("Find Closest Players", id="submit-button", n_clicks=0)
    ], className="button-column"),

    html.Div(id="closest-players-output", className="scroll-table"),
    html.Div(id="averaged-metrics-output", className="averages-row")
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

        distances_df = calculate_player_distances(merged_df, player_input)
        top_names = distances_df.head(6)['PLAYER_NAME'].tolist()
        top_df = merged_df[merged_df['PLAYER_NAME'].isin(top_names)]

        # Table display
        display_cols = top_df.columns
        table_rows = [html.Tr([html.Th("#")] + [html.Th(col) for col in display_cols])]
        for i, (_, row) in enumerate(top_df.iterrows(), 1):
            row_cells = [html.Td(f"{i}.")] + [html.Td(str(row[col]) if pd.notna(row[col]) else "—") for col in display_cols]
            table_rows.append(html.Tr(row_cells))
        player_table = html.Table(table_rows, className="data-table")

        # Horizontal averages
        numeric_df = top_df.select_dtypes(include='number')
        avg_values = numeric_df.mean().round(2)
        average_display = html.Div([
            html.Div([
                html.Div(f"{col}", className="metric-label"),
                html.Div(f"{val}", className="metric-value")
            ], className="metric-box") for col, val in avg_values.items()
        ], className="averages-container")

        return player_table, average_display

    return "", ""

if __name__ == "__main__":
    app.run(debug=True)
