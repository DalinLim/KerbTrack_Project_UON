from dash import html, dcc

navbar = html.Nav(
    className="bg-emerald-700",
    children=[
        html.Div(
            className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
            children=[
                html.Div(
                    className="flex justify-between h-16",
                    children=[
                        html.Div(
                            className="flex items-center",
                            children=[
                                html.Img(
                                    src="/assets/logo.png",
                                    className="h-10 w-10",
                                    alt="Logo",
                                ),
                                dcc.Link(
                                    "KerbTrack",
                                    href="/",
                                    className="text-white text-xl font-bold ml-4",
                                    refresh=False,
                                ),
                            ],
                        ),
                        html.Div(
                            className="hidden md:flex space-x-4 mt-2",
                            children=[
                                dcc.Link(
                                    "Dashboard",
                                    href="/",
                                    className="text-white hover:bg-emerald-800 px-3 py-2 rounded-md text-sm font-medium",
                                    refresh=False,
                                ),
                                dcc.Link(
                                    "Team",
                                    href="/team",
                                    className="text-white hover:bg-emerald-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium",
                                    refresh=False,
                                ),
                            ],
                        ),
                        html.Div(
                            className="md:hidden flex items-center",
                            children=[
                                html.Button(
                                    "☰",
                                    id="menu-toggle",
                                    n_clicks=0,
                                    className="text-white text-2xl focus:outline-none",
                                )
                            ],
                        ),
                    ],
                )
            ],
        ),
        html.Div(
            id="mobile-menu",
            className="md:hidden hidden px-2 pt-2 pb-3 space-y-1",
            children=[
                dcc.Link(
                    "Dashboard",
                    href="/",
                    className="block bg-gray-900 text-white px-3 py-2 rounded-md text-base font-medium",
                    refresh=False,
                ),
                dcc.Link(
                    "Team",
                    href="/team",
                    className="block text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-base font-medium",
                    refresh=False,
                ),
                html.Button(
                    "Logout",
                    id="mobile-logout-button",
                    n_clicks=0,
                    className="block text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-base font-medium",
                ),
            ],
        ),
    ],
)
