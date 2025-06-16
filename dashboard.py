import pandas as pd
from dash import Dash, html, dcc, Input, Output, State
from utils.data_downloader import download_draft_combine_anthro_data, download_draft_combine_drill_data
from utils.data_cleaner import clean_and_merge
from utils.player_loader import load_custom_players
from components.distance_calculator import calculate_player_distances
import plotly.express as px
import plotly.graph_objects as go


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

playerStats = load_custom_players("draft_players.csv")

playerMinutes = load_custom_players("minutes_per_player.csv")

# Create lowercase temporary columns for comparison
merged_df['name_lower'] = merged_df['PLAYER_NAME'].str.lower()
playerStats['name_lower'] = playerStats['Player'].str.lower()
playerMinutes['name_lower'] = playerMinutes['Player'].str.lower()


# Perform merge on lowercase name match
final_df = merged_df.merge(
    playerStats,
    how='left',
    on='name_lower',
    suffixes=('', '_from_stats')
)
final_df = final_df.merge(
    playerMinutes[['name_lower', 'MP']],  # keep only necessary columns
    how='left',
    on='name_lower'
)

# Drop the temporary lowercase column
final_df = final_df.drop(columns=['name_lower', 'Player', 'Minutes Played'], errors='ignore')

final_df = final_df.rename(columns={'MP': 'Minutes Played Per Game'})

print("Merged DataFrame Columns:", final_df.columns.tolist())

app = Dash(__name__)

app.layout = html.Div([
    html.H1("NBA Player Comparison Dashboard", style={"textAlign": "center", "marginTop": "20px"}),

    # Player Selection + Input Fields + Button
    html.Div([
        html.Label("Select a Utah Player", style={"fontWeight": "bold"}),
        dcc.Dropdown(
            id="utah-player-dropdown",
            options=[{"label": name, "value": name} for name in utah_players["Player"]],
            placeholder="Choose a player...",
            style={"width": "100%", "marginBottom": "25px"}
        ),

        html.Div([
            html.P("Or", style={
                "textAlign": "left",
                "marginTop": "10px",
                "marginBottom": "0",
                "fontWeight": "bold",
                "fontSize": "18px"
            }),
            html.P("Manually Insert Player Metrics", style={
                "textAlign": "left",
                "marginTop": "10",
                "marginBottom": "20px",
                "fontWeight": "bold",
                "fontSize": "16px"
            })
        ]),


        html.Div([
            html.Div([
                html.Label("Height Without Shoes (inches)"),
                dcc.Input(id="height-input", type="number", placeholder="e.g., 80",
                          style={"width": "100%", "height": "30px"})
            ]),
            html.Div([
                html.Label("Wingspan (inches)"),
                dcc.Input(id="wingspan-input", type="number", placeholder="e.g., 85",
                          style={"width": "100%", "height": "30px"})
            ]),
            html.Div([
                html.Label("Standing Reach (inches)"),
                dcc.Input(id="reach-input", type="number", placeholder="e.g., 108",
                          style={"width": "100%", "height": "30px"})
            ]),
            html.Div([
                html.Label("Hand Length (inches)"),
                dcc.Input(id="hand-length-input", type="number", placeholder="e.g., 8.25",
                          style={"width": "100%", "height": "30px"})
            ]),
            html.Div([
                html.Label("Hand Width (inches)"),
                dcc.Input(id="hand-width-input", type="number", placeholder="e.g., 8.75",
                          style={"width": "100%", "height": "30px"})
            ])
        ], style={
            "display": "grid",
            "gridTemplateColumns": "1fr 1fr",
            "gap": "20px 40px",
            "marginBottom": "30px"
        }),

        html.Div([
            html.Label("Filter Players By:", style={"fontWeight": "bold", "marginBottom": "10px"}),
            dcc.Checklist(
                id="filter-checklist",
                options=[
                    {"label": "First Round Draft Picks", "value": "first_round"},
                    {"label": "Played Significant Minutes", "value": "significant_minutes"},
                    {"label": "Was Drafted", "value": "was_drafted"},
                ],
                value=[],
                labelStyle={"display": "block", "marginBottom": "5px"},
                style={"marginBottom": "20px"}
            )
        ]),

        html.Div([
            html.Button("Find Closest Players", id="submit-button", n_clicks=0,
                        style={
                            "height": "45px",
                            "padding": "0 20px",
                            "fontSize": "16px",
                            "textAlign": "center"
                        })
        ], style={"display": "flex", "justifyContent": "center"})
    ], className="section-bubble"),

    # Table Output
    html.Div([
        html.H3("Similar Players to Given Player", style={"textAlign": "center", "marginBottom": "20px"}),
        html.Div(id="closest-players-output-content")
    ], className="section-bubble"),

    # Averages
    html.Div(id="averaged-metrics-output-averages", className="section-bubble"),

    # Graphs
    html.Div(id="averaged-metrics-output-graphs", className="section-bubble")
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
    [Output("closest-players-output-content", "children"),
     Output("averaged-metrics-output-averages", "children"),
     Output("averaged-metrics-output-graphs", "children")],
    [Input("submit-button", "n_clicks")],
    [State("utah-player-dropdown", "value"),
     State("height-input", "value"),
     State("wingspan-input", "value"),
     State("reach-input", "value"),
     State("hand-length-input", "value"),
     State("hand-width-input", "value"),
     State("filter-checklist", "value")]
)

def calculate_and_display(n_clicks, player_name, height, wingspan, reach, hand_length, hand_width, filters):
    if n_clicks > 0 and all([height, wingspan, reach, hand_length, hand_width]):
        player_input = {
            'HEIGHT_WO_SHOES': height,
            'WINGSPAN': wingspan,
            'STANDING_REACH': reach,
            'HAND_LENGTH': hand_length,
            'HAND_WIDTH': hand_width
        }

        # Start with the full dataset
        filtered_df = final_df.copy()
        filtered_df['Pick'] = pd.to_numeric(filtered_df['Pick'], errors='coerce')
        filtered_df['Minutes Played Per Game'] = pd.to_numeric(filtered_df['Minutes Played Per Game'], errors='coerce')


        if "first_round" in filters:
            filtered_df = filtered_df[filtered_df['Pick'] <= 30]

        if "significant_minutes" in filters:
            filtered_df = filtered_df[filtered_df['Minutes Played Per Game'] >= 10]  # Example threshold

        if "was_drafted" in filters:
            filtered_df = filtered_df[filtered_df['Pick'].notna()]

        distances_df = calculate_player_distances(filtered_df, player_input)
        top_names = distances_df.head(6)['PLAYER_NAME'].tolist()
        top_df = filtered_df[filtered_df['PLAYER_NAME'].isin(top_names)].copy()
        top_df = top_df.merge(distances_df[['PLAYER_NAME', 'Distance']], on='PLAYER_NAME', how='left')

        display_df = top_df.drop(columns=['Distance', 'Name Lower', 'name_lower'], errors='ignore').copy()
        clean_cols = [col.replace('_', ' ').title() for col in display_df.columns]
        col_map = dict(zip(display_df.columns, clean_cols))

        display_df = display_df.rename(columns=col_map)
        display_df = display_df.rename(columns={'Pick': 'Draft Pick #'})


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
                if "Draft Pick #" in display_df.columns and pd.isna(you_row.get("Draft Pick #")):
                    you_row["Draft Pick #"] = "Undrafted"
                if 'DraftYear' in display_df.columns and pd.isna(you_row.get("DraftYear")):
                    display_df['DraftYear'] = display_df['DraftYear'].fillna("")
                if "Minutes Played Per Game" in display_df.columns and pd.isna(you_row.get("Minutes Played Per Game")):
                    you_row["Minutes Played Per Game"] = ""


            else:
                you_row.update({
                    'Height Wo Shoes': height,
                    'Wingspan': wingspan,
                    'Standing Reach': reach,
                    'Hand Length': hand_length,
                    'Hand Width': hand_width
                })
                you_row["Player Name"] = "You"
                if "Draft Pick #" in display_df.columns:
                    you_row["Draft Pick #"] = "Undrafted"
                if 'DraftYear' in display_df.columns:
                    display_df['DraftYear'] = display_df['DraftYear'].fillna("")
                if "Minutes Played Per Game" in display_df.columns:
                    you_row["Minutes Played Per Game"] = ""


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

        exclude_fields = ['Height Wo Shoes', 'Wingspan', 'Standing Reach', 'Hand Length', 'Hand Width', 'Distance', 'Draft Pick #', 'Draftyear', 'Minutes Played Per Game']
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



        utah_df = utah_players
        selected_utah_row = utah_df[utah_df['Player'] == player_name]

        selected_utah_row = selected_utah_row.rename(columns = {
            'Player': 'Player Name',
            'HEIGHT_WO_SHOES': 'Height Wo Shoes',
            'WEIGHT': 'Weight',
            'WINGSPAN': 'Wingspan',
            'STANDING_REACH': 'Standing Reach',
            'HAND_LENGTH': 'Hand Length',
            'HAND_WIDTH': 'Hand Width',
            'STANDING_VERTICAL_LEAP': 'Standing Vertical Leap',
            'MAX_VERTICAL_LEAP': 'Max Vertical Leap',
            'LANE_AGILITY_TIME': 'Lane Agility Time',
            'MODIFIED_LANE_AGILITY_TIME': 'Modified Lane Agility Time',
            'THREE_QUARTER_SPRINT': 'Three Quarter Sprint',
            'BENCH_PRESS': 'Bench Press'
        })

        

        graphs = []
        
        for col in numeric_df.columns:
            
            full_y = pd.concat([selected_utah_row[['Player Name', col]], display_df[['Player Name', col]]])
            y_values = full_y[col]

            player_name_col = full_y['Player Name']

            sorted_vals = sorted(y_values.dropna())
            y_min = sorted_vals[1] * 0.85 if len(sorted_vals) >= 2 and sorted_vals[0] == 0 else (sorted_vals[0] * 0.95 if sorted_vals else 0)
            y_max = max(sorted_vals) * 1.15 if sorted_vals else 1

            # Create color list: first bar red, rest steelblue
            colors = ['#BE0000'] + ['steelblue'] * (len(full_y) - 1)

            fig = go.Figure(data=[
                go.Bar(
                    x=full_y['Player Name'],
                    y=[v if v != "N/A" else 0 for v in full_y[col]],
                    marker_color=colors,
                    text=full_y[col],  
                    textposition='outside' 
                )
            ])

            fig.update_layout(
                title=col,
                height=300,
                yaxis=dict(range=[y_min, y_max]),
                xaxis_title='Player Name',
                yaxis_title=col
            )


            graphs.append(dcc.Graph(figure=fig))

        graph_section = html.Div([
            html.H3("Metric Comparisons Across Closest Players", style={"textAlign": "center", "marginTop": "40px"}),
            html.Div(graphs)
        ])

        return player_table, averages_section, graph_section


    return "", "", ""