import dash
from dash import html, dcc, Input, Output, State, callback


login_layout = html.Div(className="min-h-screen flex items-center justify-center bg-gray-100", children=[
    html.Div(className="bg-white p-8 rounded shadow-md w-full max-w-sm", children=[
        html.H2("Login", className="text-2xl font-bold mb-4 text-center"),
        dcc.Input(id="login-username", type="text", placeholder="Username", className="w-full p-2 mb-4 border rounded"),
        
        # Wrap password input and toggle button in a div with relative positioning
        html.Div([
            dcc.Input(
                id="login-password",
                type="password",
                placeholder="Password",
                className="w-full p-2 mb-4 border rounded pr-12"
            ),
            html.Button(
                "Show",
                id="toggle-password",
                n_clicks=0,
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-transparent border-none cursor-pointer p-1 text-sm"
            )
        ], style={"position": "relative"}),
        
        html.Button("Login", id="login-button", n_clicks=0, className="w-full bg-emerald-600 text-white p-2 rounded"),
        html.Div(id="login-message", className="mt-4 text-center text-red-500"),
        html.A("Don't have an account? Register", href="/register", className="text-blue-500 text-sm mt-4 block text-center")
    ])
])

# Callback to toggle password visibility and button text
@callback(
    Output("login-password", "type"),
    Output("toggle-password", "children"),
    Input("toggle-password", "n_clicks"),
    State("login-password", "type"),
)
def toggle_password_visibility(n_clicks, current_type):
    if n_clicks is None or n_clicks == 0:
        raise dash.exceptions.PreventUpdate
    
    if current_type == "password":
        return "text", "Hide"
    else:
        return "password", "Show"

