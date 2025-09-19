import dash
from dash import html, dcc, Output, Input, State
from layouts.login import login_layout
from layouts.register import register_layout
from layouts.team import team_layout
from layouts.home import home_layout, register_callbacks
import paho.mqtt.client as mqtt
import threading
import json

# Tailwind CSS
external_scripts = ["https://cdn.tailwindcss.com"]

app = dash.Dash(
    __name__,
    external_scripts=external_scripts,
    suppress_callback_exceptions=True
)

# Shared MQTT data store
mqtt_data = []

# MQTT setup
broker = "broker.hivemq.com"
topic = "test/kerbtrack/json_data"

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print("Received MQTT message:", data)
        mqtt_data.append(data)
        # REMOVED: if len(mqtt_data) > 30: mqtt_data.pop(0)
        # Now it keeps all data without removing oldest
    except Exception as e:
        print("MQTT error:", e)

mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(broker, 1883)
mqtt_client.subscribe(topic)

def mqtt_loop():
    mqtt_client.loop_forever()

thread = threading.Thread(target=mqtt_loop)
thread.daemon = True
thread.start()

# User
fake_users = {
    "admin_test": "admintest123",
    "dalin": "1234",
    "umair": "umair123"
}

# App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Controls navigation
    dcc.Store(id='login-state', data={'logged_in': False, 'user': None},storage_type='session'),
    html.Div(id='page-content')
])

# Login callback with redirect
@app.callback(
    Output('login-state', 'data'),
    Output('login-message', 'children'),
    Output('url', 'pathname'),  # Redirect to "/"
    Input('login-button', 'n_clicks'),
    State('login-username', 'value'),
    State('login-password', 'value'),
    prevent_initial_call=True,
    allow_duplicate=True
)

#login button
def handle_login(n_clicks, username, password):
    # Check if username or password is empty or None
    if not username or not password:
        return {'logged_in': False, 'user': None}, "Please enter username and password", dash.no_update

    # Check users
    if username in fake_users and password == fake_users[username]:
        return {'logged_in': True, 'user': username}, "", "/"
    else:
        return {'logged_in': False, 'user': None}, "Invalid username or password", dash.no_update


# This is where your page routing callback goes:
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('login-state', 'data')
)
def display_page(pathname, login_data):
    logged_in = login_data.get('logged_in', False)
    user = login_data.get('user', None)

    if pathname == '/login' or pathname is None:
        return login_layout
    elif pathname == '/register':
        return register_layout
    elif pathname == '/team':
        return team_layout
    elif pathname == '/' and logged_in:
        return html.Div([
            html.H1(f"Welcome, {user}!", className="text-xl font-bold text-center mt-4"),
            home_layout
        ])
    elif pathname == '/' and not logged_in:
        return dcc.Location(pathname="/login", id="redirect-login")
    else:
        return html.Div([
            html.H1("404 - Page Not Found", className="text-red-500 text-2xl font-bold text-center mt-10"),
            html.A("Back to Home", href="/", className="block text-center mt-4 text-emerald-600 underline")
        ])

#logout
# Add this callback to app.py, along with the existing callbacks
# @app.callback(
#     Output('login-state', 'data', allow_duplicate=True),
#     Output('url', 'pathname', allow_duplicate=True),
#     Input('logout-button', 'n_clicks'),
#     Input('mobile-logout-button', 'n_clicks'),
#     State('login-state', 'data'),
#     prevent_initial_call=True
# )
# def handle_logout(n_clicks, mobile_n_clicks, login_data):
#     ctx = dash.callback_context
    
#     if not ctx.triggered:
#         return dash.no_update, dash.no_update
    
#     # Check which logout button was clicked
#     button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
#     if button_id in ['logout-button', 'mobile-logout-button']:
#         # Clear the login state
#         return {'logged_in': False, 'user': None}, "/login"
    
#     return dash.no_update, dash.no_update

# Optional: mobile menu toggle
@app.callback(
    Output("mobile-menu", "className"),
    Input("menu-toggle", "n_clicks"),
    State("mobile-menu", "className"),
    prevent_initial_call=True
)
def toggle_menu(n_clicks, current_class):
    if "hidden" in current_class:
        return current_class.replace("hidden", "").strip()
    else:
        return current_class + " hidden"

# Register MQTT-dependent callbacks (if any)
register_callbacks(app, mqtt_data)

if __name__ == '__main__':
    app.run(debug=True)