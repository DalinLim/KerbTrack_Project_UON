from dash import html

footer = html.Footer(
    className="bg-emerald-700 text-white",  # Matching the navbar color scheme
    children=[
        html.Div(
            className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6",  # Same container width as navbar
            children=[
                html.Div(
                    className="flex flex-col md:flex-row justify-between items-center",
                    children=[
                        # Left side - Branding
                        html.Div(
                            className="flex items-center mb-4 md:mb-0",
                            children=[
                                html.Img(
                                    src="/assets/logo.png",
                                    className="h-8 w-8",  # Slightly smaller than navbar logo
                                    alt="Logo"
                                ),
                                html.Div(
                                    className="ml-3",
                                    children=[
                                        html.Div("KerbTrack", className="text-sm font-bold"),
                                        html.Div(
                                            "© 2025 All Rights Reserved",
                                            className="text-xs text-emerald-100"
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        # Middle - Quick links (desktop)
                        html.Div(
                            className="hidden md:flex space-x-6",
                            children=[
                                html.A("About", href="#", className="text-emerald-100 hover:text-white text-sm"),
                                html.A("Privacy", href="#", className="text-emerald-100 hover:text-white text-sm"),
                                html.A("Licensing", href="#", className="text-emerald-100 hover:text-white text-sm"),
                                html.A("Contact", href="#", className="text-emerald-100 hover:text-white text-sm")
                            ]
                        ),
                        
                        # Right side - Social/action
                        html.Div(
                            className="flex space-x-4",
                            children=[
                                html.A(
                                    html.I(className="fab fa-twitter text-lg hover:text-emerald-200"),
                                    href="#",
                                    target="_blank"
                                ),
                                html.A(
                                    html.I(className="fab fa-linkedin text-lg hover:text-emerald-200"),
                                    href="#",
                                    target="_blank"
                                ),
                                html.A(
                                    html.I(className="fab fa-github text-lg hover:text-emerald-200"),
                                    href="#",
                                    target="_blank"
                                )
                            ]
                        ),
                        
                        # Mobile quick links
                        html.Div(
                            className="md:hidden w-full mt-4 pt-4 border-t border-emerald-600",
                            children=[
                                html.Div(
                                    className="grid grid-cols-2 gap-4",
                                    children=[
                                        html.A("About", href="#", className="text-emerald-100 hover:text-white text-sm"),
                                        html.A("Privacy", href="#", className="text-emerald-100 hover:text-white text-sm"),
                                        html.A("Licensing", href="#", className="text-emerald-100 hover:text-white text-sm"),
                                        html.A("Contact", href="#", className="text-emerald-100 hover:text-white text-sm")
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)