import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import Dash, dcc, html, Input, Output, State, ALL, ctx
import numpy as np
from conversation import Transcript, Summary

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)


summary_lines = []
transcript = Transcript("ELITR Minuting Corpus/ELITR-minuting-corpus/elitr-minuting-corpus-en/dev/meeting_en_dev_009/transcript_MAN_annot09.txt")
summary = Summary("ELITR Minuting Corpus/ELITR-minuting-corpus/elitr-minuting-corpus-en/dev/meeting_en_dev_009/minutes_GENER_annot09.txt")

from sentence_transformers import SentenceTransformer, util
import torch

transcript_embeddings = torch.load("transcript.pt")
summary_embeddings = torch.load("summary.pt")
#Compute cosine-similarities
cosine_scores = util.cos_sim(summary_embeddings, transcript_embeddings)

light_colors = [
    "#FFCCCC",  # Light Coral
    "#FFE6CC",  # Light Apricot
    "#FFFFCC",  # Light Yellow
    "#CCFFCC",  # Light Mint
    "#CCFFFF",  # Light Sky Blue
    "#E6CCFF",  # Light Lavender
    "#F2F2F2",  # Light Gray
    "#F5F5F5",  # White Smoke
    "#F0FFFF",  # Azure
    "#F0F8FF"   # Alice Blue
]

speaker_mapping = {}
for i, speaker in enumerate(transcript.speakers):
    speaker_mapping[speaker] = i

messages = []
for line in transcript.lines:
    messages.append(html.Div(line.content, className="d-flex rounded p-2 border shadow-sm", style={"background-color":light_colors[speaker_mapping[line.speaker]]}))

def messages_sim(indices):
    messages = []
    checked_indices = []
    for i in indices:
        if i in checked_indices:
            continue
        for j in range(-3,4,1):
            if i + j < 0:
                continue
            opacity = 0.5
            if j+i in indices:
                opacity=1
            line = transcript.lines[i+j]
            messages.append(html.Div(line.content, className="d-flex rounded p-2 border shadow-sm", 
                                     style={"background-color":light_colors[speaker_mapping[line.speaker]], 
                                            "opacity":opacity}))
            checked_indices.append(j+i)
        messages.append(html.Hr())
    return messages

for i, line in enumerate(summary.lines):
    if line.count(", ") >= 1:
        summary_lines.append(html.Div([html.Div(f"{sentence}. ") for sentence in line.split(". ")], className="d-flex flex-row",
                                      id={"type":"summary-line", "index":i}))
    else:
        summary_lines.append(html.Div(line, id={"type":"summary-line", "index":i}))
summary_lines = html.Div(summary_lines, className="d-flex flex-column gap-2")

app.layout = html.Div([
    html.Div([
        dbc.Input(placeholder="username"),
        dbc.Input(placeholder="password"),
        dbc.Button("Login")
    ], className="d-flex flex-row gap-2 p-1", style={"background-color":"#6b757b"}),
    html.Div(
        [
            html.Div(
                [
                    html.Div("Transcription", className="fs-3"),
                    html.Div(messages, id="transcript", className="d-flex flex-column gap-2 rounded border p-3 bg-white shadow-sm", 
                             style={"width":"38vw", "height":"90vh", "overflow-y":"scroll"})
                ], className="d-flex flex-column"),
            html.Div(
                [
                html.Div("Summary", className="fs-3"),
                html.Div(id="dummy"),
                html.Div(
                        [
                            summary_lines
                        ], id="summary", style={"width":"60vw", "height":"90vh", "overflow-y":"scroll"}, 
                        className="rounded border shadow-sm bg-white p-3")
                ], className="d-flex flex-column")
        ], className="d-flex flex-row gap-2 p-2", style={"background-color":"#fafafa"})
], className="d-flex flex-column gap-2", style={"background-color":"#fafafa"})

@app.callback(
    Output("transcript", "children"),
    Input({"type":"summary-line", "index":ALL}, "n_clicks"),
    prevent_initial_call=True
)
def update_line_number(n):
    if n:
        line_number = int(ctx.triggered_id["index"])
        similar_lines_indices = np.where(cosine_scores[line_number] > 0.5)[0].tolist()
        return messages_sim(similar_lines_indices)
if __name__ == "__main__":
    app.run_server(debug=True)