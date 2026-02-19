import hmac
import os

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html
from flask import Response, request
from sqlalchemy import create_engine, text


def get_database_url() -> str:
    default = "postgresql://premiere:premierepass@db:5432/premiereaesthetics"
    url = os.getenv("DATABASE_URL", default)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


ENGINE = create_engine(get_database_url())
DASH_USER = os.getenv("OWNER_DASH_USERNAME", "owner")
DASH_PASSWORD = os.getenv("OWNER_DASH_PASSWORD", "change-me")
DASH_URL_BASE_PATHNAME = os.getenv("DASH_URL_BASE_PATHNAME", "/")


def normalize_base_path(path_value: str) -> str:
    path = (path_value or "/").strip()
    if not path.startswith("/"):
        path = f"/{path}"
    if not path.endswith("/"):
        path = f"{path}/"
    return path


DASH_BASE_PATH = normalize_base_path(DASH_URL_BASE_PATHNAME)


def load_events_df() -> pd.DataFrame:
    query = text(
        """
        SELECT event_type, element, page, timestamp
        FROM core_event
        ORDER BY timestamp DESC
        LIMIT 5000
        """
    )
    try:
        with ENGINE.connect() as conn:
            df = pd.read_sql(query, conn)
    except Exception:
        df = pd.DataFrame(columns=["event_type", "element", "page", "timestamp"])

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["day"] = df["timestamp"].dt.date
    return df


app = Dash(
    __name__,
    requests_pathname_prefix=DASH_BASE_PATH,
    routes_pathname_prefix=DASH_BASE_PATH,
)
app.title = "Premiere Aesthetics Analytics"


def is_authorized(username: str, password: str) -> bool:
    return hmac.compare_digest(username, DASH_USER) and hmac.compare_digest(password, DASH_PASSWORD)


@app.server.before_request
def require_basic_auth():
    auth = request.authorization
    if auth and is_authorized(auth.username, auth.password):
        return None
    return Response(
        "Authentication required.",
        401,
        {"WWW-Authenticate": 'Basic realm="Premiere Analytics"'},
    )

app.layout = html.Div(
    [
        html.H1("Premiere Aesthetics - Event Dashboard"),
        html.P("Actualizare automata la 60 de secunde"),
        dcc.Interval(id="refresh", interval=60_000, n_intervals=0),
        html.Div(id="metrics", style={"display": "flex", "gap": "18px", "flexWrap": "wrap"}),
        dcc.Graph(id="events_by_day"),
        dcc.Graph(id="top_event_types"),
        dcc.Graph(id="top_elements"),
    ],
    style={
        "fontFamily": "Manrope, sans-serif",
        "padding": "24px",
        "background": "linear-gradient(130deg, #0b1620, #11283b)",
        "minHeight": "100vh",
        "color": "#f5f7fa",
    },
)


@app.callback(
    Output("metrics", "children"),
    Output("events_by_day", "figure"),
    Output("top_event_types", "figure"),
    Output("top_elements", "figure"),
    Input("refresh", "n_intervals"),
)
def refresh_dashboard(_):
    df = load_events_df()

    if df.empty:
        blank_fig = px.scatter(title="Nu exista date disponibile.")
        return [html.Div("0 evenimente")], blank_fig, blank_fig, blank_fig

    total_events = len(df)
    page_views = int((df["event_type"] == "page_view").sum())
    contacts = int(df["event_type"].isin(["contact_submit", "contact_form_submit"]).sum())

    by_day = df.groupby("day", as_index=False).size()
    fig_day = px.area(by_day, x="day", y="size", title="Evenimente pe zi", color_discrete_sequence=["#f2b134"])

    top_types = df.groupby("event_type", as_index=False).size().sort_values("size", ascending=False).head(10)
    fig_types = px.bar(top_types, x="event_type", y="size", title="Top tipuri de evenimente", color_discrete_sequence=["#29a89d"])

    filtered_elements = df[df["element"].astype(str).str.len() > 0]
    top_elements = filtered_elements.groupby("element", as_index=False).size().sort_values("size", ascending=False).head(10)
    fig_elements = px.bar(top_elements, x="size", y="element", orientation="h", title="Top elemente", color_discrete_sequence=["#8dd6ff"])

    metric_cards = [
        html.Div(f"Total evenimente: {total_events}", style=card_style()),
        html.Div(f"Page views: {page_views}", style=card_style()),
        html.Div(f"Contact submits: {contacts}", style=card_style()),
    ]
    return metric_cards, fig_day, fig_types, fig_elements


def card_style() -> dict:
    return {
        "background": "rgba(255,255,255,0.12)",
        "border": "1px solid rgba(255,255,255,0.24)",
        "padding": "12px 16px",
        "borderRadius": "12px",
        "backdropFilter": "blur(8px)",
        "fontWeight": "600",
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
