from dash import html, dcc

register_layout = html.Div(className="min-h-screen flex items-center justify-center bg-gray-100", children=[
    html.Div(className="bg-white p-8 rounded shadow-md w-full max-w-sm", children=[
        html.H2("Register", className="text-2xl font-bold mb-4 text-center"),
        dcc.Input(id="register-username", type="text", placeholder="Username", className="w-full p-2 mb-4 border rounded"),
        dcc.Input(id="register-password", type="password", placeholder="Password", className="w-full p-2 mb-4 border rounded"),
        html.Button("Register", id="register-button", n_clicks=0, className="w-full bg-emerald-600 text-white p-2 rounded"),
        html.Div(id="register-message", className="mt-4 text-center text-red-500"),
        html.A("Already have an account? Login", href="/login", className="text-blue-500 text-sm mt-4 block text-center")
    ])
])
