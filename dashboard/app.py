import hmac
import os
from datetime import datetime
from urllib.parse import quote, unquote

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from flask import redirect, render_template_string, request, session
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
DASH_SESSION_SECRET = os.getenv("DASH_SESSION_SECRET", os.getenv("SECRET_KEY", "change-me-dash-secret"))
DASH_URL_BASE_PATHNAME = os.getenv("DASH_URL_BASE_PATHNAME", "/")


def normalize_base_path(path_value: str) -> str:
    path = (path_value or "/").strip()
    if not path.startswith("/"):
        path = f"/{path}"
    if not path.endswith("/"):
        path = f"{path}/"
    return path


DASH_BASE_PATH = normalize_base_path(DASH_URL_BASE_PATHNAME)
LOGIN_PATH = f"{DASH_BASE_PATH}login/"
LOGOUT_PATH = f"{DASH_BASE_PATH}logout/"

# Make routing deterministic even if Dash pathname env vars are present.
# We read DASH_URL_BASE_PATHNAME once, then clear dash path env vars to avoid
# constructor ambiguity in newer Dash versions.
os.environ.pop("DASH_URL_BASE_PATHNAME", None)
os.environ.pop("DASH_REQUESTS_PATHNAME_PREFIX", None)
os.environ.pop("DASH_ROUTES_PATHNAME_PREFIX", None)

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
app.server.secret_key = DASH_SESSION_SECRET
app.server.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("DJANGO_SECURE_SSL", "False").lower() == "true",
)

LOGIN_TEMPLATE = """
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Dashboard Login</title>
  <style>
    :root {
      --bg: #050505;
      --panel: rgba(13, 13, 13, 0.88);
      --border: rgba(255, 255, 255, 0.16);
      --text: #f7f7f7;
      --muted: rgba(255, 255, 255, 0.75);
      --accent: #b3001b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Sora, Manrope, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at 82% 12%, rgba(179, 0, 27, 0.28), transparent 40%),
        linear-gradient(180deg, #030303, #0b0b0b);
      display: grid;
      place-items: center;
      padding: 20px;
    }
    .panel {
      width: min(460px, 100%);
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 26px 24px;
      backdrop-filter: blur(8px);
    }
    .badge {
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid rgba(179, 0, 27, 0.45);
      background: rgba(179, 0, 27, 0.14);
      font-size: 0.72rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 10px;
    }
    h1 {
      margin: 0 0 6px;
      font-size: clamp(1.55rem, 4vw, 2rem);
      line-height: 1.12;
    }
    p { margin: 0 0 16px; color: var(--muted); }
    label {
      display: block;
      font-size: 0.82rem;
      color: var(--muted);
      margin-bottom: 6px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    input {
      width: 100%;
      height: 46px;
      border-radius: 11px;
      border: 1px solid var(--border);
      background: rgba(255, 255, 255, 0.03);
      color: var(--text);
      padding: 0 12px;
      margin-bottom: 14px;
      font-size: 0.98rem;
    }
    input:focus {
      outline: 2px solid rgba(179, 0, 27, 0.74);
      border-color: rgba(179, 0, 27, 0.74);
    }
    button {
      width: 100%;
      height: 48px;
      border: 0;
      border-radius: 11px;
      background: linear-gradient(145deg, #7a0012, #b3001b);
      color: #fff;
      font-weight: 700;
      letter-spacing: 0.02em;
      cursor: pointer;
      transition: transform 180ms ease, filter 180ms ease;
    }
    button:hover { transform: translateY(-1px); filter: brightness(1.05); }
    .error {
      border: 1px solid rgba(255, 90, 110, 0.5);
      background: rgba(179, 0, 27, 0.16);
      color: #ffd7dd;
      border-radius: 10px;
      padding: 10px 12px;
      margin-bottom: 12px;
      font-size: 0.92rem;
    }
  </style>
</head>
<body>
  <main class="panel">
    <span class="badge">Private Analytics</span>
    <h1>Dashboard Login</h1>
    <p>Autentificare pentru acces la statistici si evenimente.</p>
    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}
    <form method="post" action="{{ login_path }}">
      <input type="hidden" name="next" value="{{ next_path }}" />
      <label for="username">Username</label>
      <input id="username" type="text" name="username" autocomplete="username" required />
      <label for="password">Password</label>
      <input id="password" type="password" name="password" autocomplete="current-password" required />
      <button type="submit">Autentificare</button>
    </form>
  </main>
</body>
</html>
"""

THEME = {
    "bg": "#050505",
    "bg_gradient": "radial-gradient(circle at 86% 12%, rgba(179, 0, 27, 0.24), transparent 38%), linear-gradient(180deg, #030303, #0a0a0a)",
    "panel": "rgba(12, 12, 12, 0.86)",
    "panel_soft": "rgba(18, 18, 18, 0.72)",
    "border": "rgba(255, 255, 255, 0.14)",
    "grid": "rgba(255, 255, 255, 0.14)",
    "text": "#f7f7f7",
    "text_muted": "rgba(255, 255, 255, 0.76)",
    "accent": "#b3001b",
    "accent_soft": "rgba(179, 0, 27, 0.35)",
}

APP_STYLE = {
    "fontFamily": "Sora, Manrope, sans-serif",
    "padding": "28px",
    "background": THEME["bg_gradient"],
    "minHeight": "100vh",
    "color": THEME["text"],
}

PANEL_STYLE = {
    "background": THEME["panel"],
    "border": f"1px solid {THEME['border']}",
    "borderRadius": "18px",
    "padding": "12px 14px",
    "backdropFilter": "blur(8px)",
}

METRIC_GRID_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
    "gap": "14px",
    "marginBottom": "16px",
}

GRAPH_GRID_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(340px, 1fr))",
    "gap": "16px",
}


def is_authorized(username: str, password: str) -> bool:
    return hmac.compare_digest(username, DASH_USER) and hmac.compare_digest(password, DASH_PASSWORD)


@app.server.before_request
def require_dashboard_login():
    path = request.path or "/"
    if not path.startswith(DASH_BASE_PATH):
        return None
    if path.startswith(LOGIN_PATH) or path.startswith(LOGOUT_PATH):
        return None
    if session.get("dash_authenticated"):
        return None

    next_target = request.full_path if request.query_string else path
    encoded_next = quote(next_target, safe="/?=&")
    return redirect(f"{LOGIN_PATH}?next={encoded_next}")


def safe_next_path(next_path: str | None) -> str:
    raw = (next_path or "").strip()
    if not raw:
        return DASH_BASE_PATH
    decoded = unquote(raw)
    if not decoded.startswith(DASH_BASE_PATH):
        return DASH_BASE_PATH
    return decoded


@app.server.route(LOGIN_PATH, methods=["GET", "POST"])
def dashboard_login():
    error = ""
    next_path = safe_next_path(request.values.get("next"))
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if is_authorized(username, password):
            session["dash_authenticated"] = True
            return redirect(next_path)
        error = "Credentiale invalide. Verifica username si parola."
    return render_template_string(LOGIN_TEMPLATE, error=error, next_path=next_path, login_path=LOGIN_PATH)


@app.server.route(LOGOUT_PATH, methods=["GET"])
def dashboard_logout():
    session.clear()
    return redirect(LOGIN_PATH)

app.layout = html.Div(
    [
        html.Div(
            [
                html.Span(
                    "Private Analytics",
                    style={
                        "display": "inline-block",
                        "padding": "6px 10px",
                        "borderRadius": "999px",
                        "fontSize": "0.75rem",
                        "letterSpacing": "0.08em",
                        "textTransform": "uppercase",
                        "border": f"1px solid {THEME['accent_soft']}",
                        "background": "rgba(179, 0, 27, 0.14)",
                        "color": THEME["text"],
                        "marginBottom": "10px",
                    },
                ),
                html.H1(
                    "Premiere Aesthetics Dashboard",
                    style={
                        "margin": "0 0 8px",
                        "fontSize": "clamp(1.6rem, 2.8vw, 2.4rem)",
                        "lineHeight": "1.1",
                    },
                ),
                html.P(
                    "Trafic, interactiuni si conversii. Date actualizate automat la fiecare 60 secunde.",
                    id="dashboardStatus",
                    style={"margin": 0, "color": THEME["text_muted"], "fontSize": "0.96rem"},
                ),
                html.A(
                    "Deconectare",
                    href=LOGOUT_PATH,
                    style={
                        "display": "inline-block",
                        "marginTop": "12px",
                        "fontSize": "0.85rem",
                        "textDecoration": "none",
                        "color": THEME["text"],
                        "padding": "8px 12px",
                        "border": f"1px solid {THEME['border']}",
                        "borderRadius": "10px",
                        "background": "rgba(255, 255, 255, 0.03)",
                    },
                ),
            ],
            style={
                "marginBottom": "20px",
                "background": THEME["panel_soft"],
                "border": f"1px solid {THEME['border']}",
                "borderRadius": "20px",
                "padding": "18px 20px",
            },
        ),
        dcc.Interval(id="refresh", interval=60_000, n_intervals=0),
        html.Div(id="metrics", style=METRIC_GRID_STYLE),
        html.Div(
            [
                html.Div([dcc.Graph(id="events_by_day", config={"displaylogo": False})], style=PANEL_STYLE),
                html.Div([dcc.Graph(id="top_event_types", config={"displaylogo": False})], style=PANEL_STYLE),
            ],
            style=GRAPH_GRID_STYLE,
        ),
        html.Div([dcc.Graph(id="top_elements", config={"displaylogo": False})], style={**PANEL_STYLE, "marginTop": "16px"}),
    ],
    style=APP_STYLE,
)


@app.callback(
    Output("metrics", "children"),
    Output("dashboardStatus", "children"),
    Output("events_by_day", "figure"),
    Output("top_event_types", "figure"),
    Output("top_elements", "figure"),
    Input("refresh", "n_intervals"),
)
def refresh_dashboard(_):
    df = load_events_df()
    refreshed_at = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    if df.empty:
        blank_fig = empty_figure("Nu exista date disponibile inca.")
        cards = [
            metric_card("Total evenimente", "0", emphasize=True),
            metric_card("Page views", "0"),
            metric_card("Formulare trimise", "0"),
            metric_card("Pagini unice", "0"),
        ]
        return cards, f"Actualizat la {refreshed_at} · Fara evenimente inregistrate.", blank_fig, blank_fig, blank_fig

    total_events = len(df)
    page_views = int((df["event_type"] == "page_view").sum())
    contacts = int(df["event_type"].isin(["contact_submit", "contact_form_submit"]).sum())
    unique_pages = int(df["page"].nunique())
    unique_elements = int(df[df["element"].astype(str).str.len() > 0]["element"].nunique())

    by_day = df.groupby("day", as_index=False).size()
    fig_day = px.area(by_day, x="day", y="size", color_discrete_sequence=[THEME["accent"]])
    fig_day.update_traces(line={"width": 2.6}, fillcolor="rgba(179, 0, 27, 0.28)")
    style_figure(fig_day, "Evenimente pe Zi")
    fig_day.update_xaxes(title=None)
    fig_day.update_yaxes(title="Evenimente")

    top_types = df.groupby("event_type", as_index=False).size().sort_values("size", ascending=False).head(10)
    fig_types = px.bar(top_types, x="event_type", y="size", color_discrete_sequence=[THEME["accent"]])
    fig_types.update_traces(marker_line_color="rgba(255,255,255,0.34)", marker_line_width=1.0)
    style_figure(fig_types, "Top Tipuri de Evenimente")
    fig_types.update_xaxes(title=None, tickangle=-24, automargin=True)
    fig_types.update_yaxes(title="Numar")

    filtered_elements = df[df["element"].astype(str).str.len() > 0]
    top_elements = filtered_elements.groupby("element", as_index=False).size().sort_values("size", ascending=False).head(10)
    fig_elements = px.bar(top_elements, x="size", y="element", orientation="h", color_discrete_sequence=[THEME["accent"]])
    fig_elements.update_traces(marker_line_color="rgba(255,255,255,0.3)", marker_line_width=1.0)
    style_figure(fig_elements, "Top Elemente Clickuite")
    fig_elements.update_xaxes(title="Click-uri")
    fig_elements.update_yaxes(title=None, automargin=True, categoryorder="total ascending")

    metric_cards = [
        metric_card("Total evenimente", format_number(total_events), emphasize=True),
        metric_card("Page views", format_number(page_views)),
        metric_card("Formulare trimise", format_number(contacts)),
        metric_card("Pagini unice", format_number(unique_pages)),
        metric_card("Elemente unice", format_number(unique_elements)),
    ]
    status = f"Actualizat la {refreshed_at} · Ultimele {format_number(total_events)} evenimente analizate."
    return metric_cards, status, fig_day, fig_types, fig_elements


def metric_card(label: str, value: str, emphasize: bool = False) -> html.Div:
    accent_border = "rgba(179, 0, 27, 0.66)" if emphasize else THEME["border"]
    accent_bg = "rgba(179, 0, 27, 0.14)" if emphasize else THEME["panel_soft"]
    return html.Div(
        [
            html.P(
                label,
                style={
                    "margin": "0 0 8px",
                    "fontSize": "0.82rem",
                    "letterSpacing": "0.06em",
                    "textTransform": "uppercase",
                    "color": THEME["text_muted"],
                    "fontWeight": "600",
                },
            ),
            html.P(
                value,
                style={"margin": 0, "fontSize": "1.56rem", "fontWeight": "700", "lineHeight": "1"},
            ),
        ],
        style={
            "background": accent_bg,
            "border": f"1px solid {accent_border}",
            "padding": "14px 16px",
            "borderRadius": "14px",
            "backdropFilter": "blur(6px)",
        },
    )


def style_figure(fig: go.Figure, title: str) -> None:
    fig.update_layout(
        title={"text": title, "x": 0.01, "xanchor": "left", "font": {"size": 22, "color": THEME["text"]}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,10,10,0.78)",
        font={"family": "Sora, Manrope, sans-serif", "size": 13, "color": THEME["text"]},
        margin={"l": 52, "r": 18, "t": 72, "b": 44},
        hoverlabel={"bgcolor": "#101010", "bordercolor": THEME["accent"], "font": {"color": THEME["text"]}},
    )
    fig.update_xaxes(showgrid=True, gridcolor=THEME["grid"], zeroline=False, tickfont={"color": THEME["text_muted"]})
    fig.update_yaxes(showgrid=True, gridcolor=THEME["grid"], zeroline=False, tickfont={"color": THEME["text_muted"]})


def empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 17, "color": THEME["text_muted"]},
    )
    style_figure(fig, "Fara date")
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def format_number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
