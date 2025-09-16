# -----------------------------
# EPL Player Dashboard (Dash)
# -----------------------------
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# 1️⃣ Load dataset
csv_path = r"C:\Users\Saif\Documents\Premier League Data\premier-player-23-24.csv"
df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip().str.replace(' ', '_')

# 2️⃣ Filter regular players
MINUTES_THRESHOLD = 900
df = df[df['Min'] >= MINUTES_THRESHOLD]

# 3️⃣ Per-90 metrics
df['Goals_per_90'] = df['Gls_90']
df['Assists_per_90'] = df['Ast_90']
df['Contribution_per_90'] = df['G+A_90']
df['xG_xAG_per_90'] = df['xG+xAG_90']
df['Performance_vs_Expected'] = df['Contribution_per_90'] - df['xG_xAG_per_90']

# 4️⃣ Contribution Score
df['Goals_norm'] = (df['Goals_per_90'] - df['Goals_per_90'].min()) / (df['Goals_per_90'].max() - df['Goals_per_90'].min())
df['Assists_norm'] = (df['Assists_per_90'] - df['Assists_per_90'].min()) / (df['Assists_per_90'].max() - df['Assists_per_90'].min())
df['Overperf_norm'] = (df['Performance_vs_Expected'] - df['Performance_vs_Expected'].min()) / (df['Performance_vs_Expected'].max() - df['Performance_vs_Expected'].min())
df['Contribution_Score'] = df['Goals_norm'] + df['Assists_norm'] + df['Overperf_norm']

# 5️⃣ Initialize Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("EPL Player Performance Dashboard", style={'textAlign': 'center'}),
    
    html.Div([
        html.Label("Select Team:"),
        dcc.Dropdown(
            options=[{'label': team, 'value': team} for team in sorted(df['Team'].unique())] + [{'label': 'All', 'value': 'All'}],
            value='All',
            id='team-dropdown'
        )
    ], style={'width': '30%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("Select Position:"),
        dcc.Dropdown(
            options=[{'label': pos, 'value': pos} for pos in sorted(df['Pos'].unique())] + [{'label': 'All', 'value': 'All'}],
            value='All',
            id='position-dropdown'
        )
    ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '20px'}),
    
    dcc.Graph(id='top-goals-chart'),
    dcc.Graph(id='top-assists-chart'),
    dcc.Graph(id='overperforming-chart'),
    dcc.Graph(id='contribution-score-chart')
])

# 6️⃣ Callback
@app.callback(
    [Output('top-goals-chart', 'figure'),
     Output('top-assists-chart', 'figure'),
     Output('overperforming-chart', 'figure'),
     Output('contribution-score-chart', 'figure')],
    [Input('team-dropdown', 'value'),
     Input('position-dropdown', 'value')]
)
def update_charts(selected_team, selected_position):
    filtered_df = df.copy()
    
    if selected_team != 'All':
        filtered_df = filtered_df[filtered_df['Team'] == selected_team]
    if selected_position != 'All':
        filtered_df = filtered_df[filtered_df['Pos'] == selected_position]
    
    # Top Goals per 90
    top_goals = filtered_df.sort_values('Goals_per_90', ascending=False).head(10)
    fig_goals = px.bar(top_goals, x='Goals_per_90', y='Player', orientation='h',
                       title='Top 10 Players by Goals per 90', text='Goals_per_90')
    fig_goals.update_layout(yaxis={'categoryorder':'total ascending'})
    
    # Top Assists per 90
    top_assists = filtered_df.sort_values('Assists_per_90', ascending=False).head(10)
    fig_assists = px.bar(top_assists, x='Assists_per_90', y='Player', orientation='h',
                         title='Top 10 Players by Assists per 90', text='Assists_per_90')
    fig_assists.update_layout(yaxis={'categoryorder':'total ascending'})
    
    # Top Overperformers
    overperformers = filtered_df.sort_values('Performance_vs_Expected', ascending=False).head(10)
    fig_over = px.bar(overperformers, x='Performance_vs_Expected', y='Player', orientation='h',
                      color='Team', text='Performance_vs_Expected', title='Top 10 Overperforming Players vs xG+xAG')
    fig_over.update_layout(yaxis={'categoryorder':'total ascending'})
    
    # Top Contribution Score
    top_score = filtered_df.sort_values('Contribution_Score', ascending=False).head(10)
    fig_score = px.bar(top_score, x='Contribution_Score', y='Player', orientation='h',
                       color='Team', text='Contribution_Score', title='Top 10 Players by Contribution Score')
    fig_score.update_layout(yaxis={'categoryorder':'total ascending'})
    
    return fig_goals, fig_assists, fig_over, fig_score

# 7️⃣ Run app
if __name__ == '__main__':
    app.run(debug=True)
