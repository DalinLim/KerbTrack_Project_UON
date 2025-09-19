import dash
from dash import html, dcc, dash_table, Output, Input, State
import pandas as pd
import dash_leaflet as dl
from components.navbar import navbar
from components.footer import footer
import os
import threading
import time
import hashlib
import atexit

# Table columns - Added Image Description column
DEFAULT_COLUMNS = [
    {"name": "ID", "id": "ID"},
    {"name": "GPS", "id": "GPS"},
    {"name": "Address", "id": "Address"},
    {"name": "Message", "id": "Message"},
    {"name": "Image", "id": "Image", "presentation": "markdown"},
    {"name": "Image Description", "id": "Image_Description"}  # New column
]

# Excel file path
EXCEL_FILE_PATH = "mqtt_data.xlsx"

# Global variables for tracking saves
mqtt_data = []  # This is MQTT data source

def parse_gps(gps_str):
    try:
        lat_str, lon_str = gps_str.split(",")
        lat_value = lat_str.strip().replace("°", "").replace(" ", "")
        lat = float(lat_value[:-1])
        if lat_value[-1].upper() == "S":
            lat = -lat
        elif lat_value[-1].upper() != "N":
            raise ValueError(f"Invalid latitude direction in '{gps_str}'")

        lon_value = lon_str.strip().replace("°", "").replace(" ", "")
        lon = float(lon_value[:-1])
        if lon_value[-1].upper() == "W":
            lon = -lon
        elif lon_value[-1].upper() != "E":
            raise ValueError(f"Invalid longitude direction in '{gps_str}'")

        return lat, lon
    except Exception as e:
        print(f"Error parsing GPS '{gps_str}': {e}")
        return None, None

def validate_data_integrity(old_df, new_df):
    """Check if critical data is being lost"""
    try:
        if not old_df.empty and not new_df.empty:
            old_ids = set(old_df['ID'].astype(str))
            new_ids = set(new_df['ID'].astype(str))
            
            lost_ids = old_ids - new_ids
            if lost_ids:
                print(f"WARNING: IDs will be lost: {lost_ids}")
                return False
        return True
    except Exception as e:
        print(f"Error validating data integrity: {e}")
        return True  # Allow save if validation fails

def save_to_excel(mqtt_data_list, max_retries=3):
    """Save MQTT data to Excel file with improved data preservation and retry mechanism"""
    for attempt in range(max_retries):
        try:
            # Create DataFrame from MQTT data
            new_df = pd.DataFrame(mqtt_data_list)
            
            if new_df.empty:
                print("No data to save")
                return True
            
            print(f"Save attempt {attempt + 1}: Processing {len(new_df)} entries")
            
            # Remove duplicates based on ID, keeping the latest entry
            initial_count = len(new_df)
            new_df = new_df.drop_duplicates(subset=['ID'], keep='last')
            if len(new_df) < initial_count:
                print(f"Removed {initial_count - len(new_df)} duplicate entries")
            
            # Sort by ID (convert to numeric for proper ordering)
            new_df['ID'] = pd.to_numeric(new_df['ID'], errors='coerce')
            new_df = new_df.sort_values('ID')
            print(f"Data sorted by ID")
                
            # Check if Excel file exists and merge intelligently
            if os.path.exists(EXCEL_FILE_PATH):
                try:
                    # Read existing Excel file
                    existing_df = pd.read_excel(EXCEL_FILE_PATH)
                    print(f"Existing Excel has {len(existing_df)} rows")
                    
                    if not existing_df.empty and 'ID' in existing_df.columns:
                        # Validate data integrity
                        validate_data_integrity(existing_df, new_df)
                        
                        # Create a mapping of ID to best Image_Description from existing file
                        description_map = {}
                        if 'Image_Description' in existing_df.columns:
                            for _, row in existing_df.iterrows():
                                row_id = str(row['ID']).strip()
                                desc = str(row['Image_Description']).strip()
                                # Keep the description if it's not empty, not nan, and not "Pending..."
                                if desc and desc != 'nan' and desc != 'Pending...':
                                    description_map[row_id] = desc
                                    print(f"Preserving description for ID {row_id}: {desc}")
                        
                        # Merge data intelligently
                        # First, add existing descriptions to new data
                        if 'Image_Description' not in new_df.columns:
                            new_df['Image_Description'] = 'Pending...'
                        
                        for idx, row in new_df.iterrows():
                            row_id = str(row['ID']).strip()
                            if row_id in description_map:
                                new_df.at[idx, 'Image_Description'] = description_map[row_id]
                                print(f"Applied saved description for ID {row_id}: {description_map[row_id]}")
                            elif pd.isna(new_df.at[idx, 'Image_Description']) or new_df.at[idx, 'Image_Description'] == 'nan':
                                new_df.at[idx, 'Image_Description'] = 'Pending...'
                        
                        # Combine with existing data, prioritizing new data for most fields but keeping existing descriptions
                        existing_df['ID'] = pd.to_numeric(existing_df['ID'], errors='coerce')
                        
                        # For entries that exist in both, keep new data but preserve non-pending descriptions
                        combined_data = []
                        new_ids = set(new_df['ID'].astype(str))
                        existing_ids = set(existing_df['ID'].astype(str))
                        
                        # Add all new entries
                        for _, row in new_df.iterrows():
                            combined_data.append(row.to_dict())
                        
                        # Add existing entries that are not in new data
                        for _, row in existing_df.iterrows():
                            if str(row['ID']) not in new_ids:
                                # Ensure all required columns exist
                                row_dict = row.to_dict()
                                if 'Image_Description' not in row_dict:
                                    row_dict['Image_Description'] = 'Pending...'
                                combined_data.append(row_dict)
                                print(f"Preserving existing entry ID {row['ID']} not in new data")
                        
                        # Create final DataFrame
                        final_df = pd.DataFrame(combined_data)
                        final_df['ID'] = pd.to_numeric(final_df['ID'], errors='coerce')
                        final_df = final_df.sort_values('ID')
                        final_df = final_df.drop_duplicates(subset=['ID'], keep='first')  # Remove any remaining duplicates
                        
                    else:
                        print("Existing Excel missing required columns or is empty")
                        if 'Image_Description' not in new_df.columns:
                            new_df['Image_Description'] = 'Pending...'
                        final_df = new_df
                        
                except Exception as e:
                    print(f"Error reading existing Excel file: {e}")
                    if 'Image_Description' not in new_df.columns:
                        new_df['Image_Description'] = 'Pending...'
                    final_df = new_df
            else:
                print("Excel file doesn't exist, creating new one")
                if 'Image_Description' not in new_df.columns:
                    new_df['Image_Description'] = 'Pending...'
                final_df = new_df
            
            # Save to Excel
            final_df.to_excel(EXCEL_FILE_PATH, index=False)
            print(f"Successfully saved {len(final_df)} entries to {EXCEL_FILE_PATH}")
            return True
            
        except Exception as e:
            print(f"Save attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in 1 second...")
                time.sleep(1)
            else:
                print("All save attempts failed!")
                import traceback
                traceback.print_exc()
                return False

def load_descriptions_from_excel():
    """Load image descriptions from Excel file"""
    try:
        if os.path.exists(EXCEL_FILE_PATH):
            print(f"Reading Excel file: {EXCEL_FILE_PATH}")
            df = pd.read_excel(EXCEL_FILE_PATH)
            print(f"Excel columns: {list(df.columns)}")
            
            if not df.empty and 'ID' in df.columns and 'Image_Description' in df.columns:
                # Convert both ID and descriptions to strings for reliable matching
                descriptions = {}
                for _, row in df.iterrows():
                    id_val = str(row['ID']).strip()
                    desc_val = str(row['Image_Description']).strip()
                    if desc_val and desc_val != 'nan' and desc_val != 'Pending...':
                        descriptions[id_val] = desc_val
                        print(f"Loaded: ID '{id_val}' -> '{desc_val}'")
                
                print(f"Total descriptions loaded: {len(descriptions)}")
                return descriptions
            else:
                print("Excel file missing required columns or is empty")
                print(f"Required: 'ID' and 'Image_Description'")
                print(f"Found: {list(df.columns)}")
        else:
            print(f"Excel file does not exist: {EXCEL_FILE_PATH}")
    except Exception as e:
        print(f"Error loading descriptions from Excel: {e}")
        import traceback
        traceback.print_exc()
    return {}

def cleanup_on_exit():
    """Save data when app shuts down"""
    try:
        if mqtt_data:
            print("App shutting down, saving final data...")
            success = save_to_excel(mqtt_data.copy())
            if success:
                print("Final save completed successfully")
            else:
                print("Final save failed")
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Register cleanup function
atexit.register(cleanup_on_exit)

# Layout
home_layout = html.Div(className="min-h-screen bg-white", children=[
    navbar,
    html.Div(id="home-page", className="relative", children=[
        html.Img(
            src="/assets/header.jpg",
            className="w-full lg:max-h-[500px] max-h-[200px] object-cover"),
        html.H1("Welcome To KerbTrack Dashboard",
                className="lg:text-4xl md:text-1sm bg-black bg-opacity-30 absolute inset-0 flex items-center justify-center font-bold text-white"),
    ]),
    html.Div(className="text-center", children=[
        html.Hr(className="mt-10 "),
        html.H1("Live Data Table", className="pt-2 text-emerald-700 font-bold text-2xl"),
        html.Div(className="border-t-4 mx-auto rounded-md border-emerald-600 w-20 my-4"),
    ]),
    html.Div(className="container justify-center mx-auto", children=[
        dcc.Store(id='mqtt-store', data=[], storage_type='memory'),
        dcc.Store(id='description-store', data={}, storage_type='memory'),  # Store for descriptions
        dcc.Interval(id='interval', interval=5000, n_intervals=0),
        dcc.Interval(id='excel-check-interval', interval=3000, n_intervals=0),  # Check Excel every 3 seconds
        html.Div(className="flex gap-2 my-2", children=[
            dcc.Input(id='search-input',
                      type='text',
                      debounce=True,
                      placeholder='Search street or suburb',
                      className="flex-grow p-2 border border-gray-300 rounded")
        ]),
        
        ## Our Table
        dash_table.DataTable(
            id='mqtt-table',
            columns=DEFAULT_COLUMNS,
            data=[],
            page_size=10,
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'fontFamily': 'Arial',
                'whiteSpace': 'normal',
                'height': 'auto',
                'backgroundColor': "#F8FAF9",
            },
            style_table={
                'maxHeight': '440px',
                'overflowY': 'auto',
                'overflowX': 'auto'
            },
            style_header={
                'backgroundColor': '#059669',
                'color': 'white',
                'fontWeight': 'bold',
                'position': 'sticky',
                'top': 0,
                'zIndex': 1
            },
            markdown_options={"html": True}
        ),
        
        ## Our Map
        html.Div(className="text-center", children=[
            html.Hr(className="mt-10 "),
            html.H1("Our Map", className="pt-2 text-emerald-700 font-bold text-2xl"),
            html.Div(className="border-t-4 mx-auto rounded-md border-emerald-600 w-20 my-4"),
        ]),
        html.Div([
            dl.Map(center=[-32.9267, 151.7789], zoom=12, children=[
                dl.TileLayer(),
                dl.LayerGroup(id="map-markers")
            ], style={'width': '100%', 'height': '500px'}),
        ]),
        html.Br(),
        html.Div(footer)
    ])
])

# Callbacks
def register_callbacks(app, mqtt_data):
    # Tracking variables for smart saving
    last_save_time = [0]
    last_data_size = [0]
    last_data_hash = ['']
    
    @app.callback(
        Output('mqtt-store', 'data'),
        Input('interval', 'n_intervals'),
        State('mqtt-store', 'data')
    )
    def update_store(n, current_data):
        current_time = time.time()
        current_size = len(mqtt_data) if mqtt_data else 0
        
        should_save = False
        save_reason = ""
        
        if mqtt_data:
            # Create hash of current data to detect changes
            try:
                data_str = str(sorted([str(item) for item in mqtt_data]))
                current_hash = hashlib.md5(data_str.encode()).hexdigest()
            except Exception as e:
                print(f"Error creating data hash: {e}")
                current_hash = str(current_time)  # Fallback
            
            # Save immediately if new data (size increased)
            if current_size > last_data_size[0]:
                should_save = True
                save_reason = f" New data detected: {current_size} items (was {last_data_size[0]})"
                last_data_size[0] = current_size
                last_data_hash[0] = current_hash
            
            # Save if data content changed (same size but different content)
            elif current_hash != last_data_hash[0]:
                should_save = True
                save_reason = " Data content changed"
                last_data_hash[0] = current_hash
            
            # Safety net: Save every 60 seconds if there's any data
            elif current_time - last_save_time[0] > 60:
                should_save = True
                save_reason = "Periodic safety backup (60s interval)"
            
            if should_save:
                def save_async():
                    print(f"Saving to Excel: {save_reason}")
                    success = save_to_excel(mqtt_data.copy())
                    if success:
                        print(f"Save completed successfully")
                    else:
                        print(f"Save failed")
                
                threading.Thread(target=save_async, daemon=True).start()
                last_save_time[0] = current_time
        
        return mqtt_data

    @app.callback(
        Output('description-store', 'data'),
        Input('excel-check-interval', 'n_intervals')
    )
    def update_descriptions(n):
        """Automatically check Excel file for updated descriptions every 3 seconds"""
        descriptions = load_descriptions_from_excel()
        return descriptions

    @app.callback(
        Output('mqtt-table', 'data'),
        Output('mqtt-table', 'columns'),
        Input('interval', 'n_intervals'),
        Input('search-input', 'value'),
        Input('description-store', 'data'),  # Listen for description updates
        State('mqtt-store', 'data')
    )
    def update_table(n, search_value, descriptions, mqtt_store_data):
        try:
            df = pd.DataFrame(mqtt_store_data)
            if df.empty:
                return [], DEFAULT_COLUMNS
            
            # Add Image column from ImageURL
            if "ImageURL" in df.columns:
                df["Image"] = df["ImageURL"].apply(lambda url: f'<a href="{url}" target="_blank">View Image</a>')  
                df.drop(columns=["ImageURL"], inplace=True)

            # Add Image_Description column with default "Pending..."
            df['Image_Description'] = 'Pending...'
            
            # Update descriptions from Excel file
            if descriptions:
                for idx, row in df.iterrows():
                    mqtt_id = str(row['ID']).strip()
                    
                    # Try to find matching description
                    if mqtt_id in descriptions:
                        df.at[idx, 'Image_Description'] = descriptions[mqtt_id]

            # Apply search filter
            if search_value:
                s = search_value.lower()
                df = df[
                    df['ID'].astype(str).str.lower().str.contains(s, na=False) |
                    df['GPS'].astype(str).str.lower().str.contains(s, na=False) |
                    df['Address'].astype(str).str.lower().str.contains(s, na=False) |
                    df['Message'].astype(str).str.lower().str.contains(s, na=False) |
                    df['Image_Description'].astype(str).str.lower().str.contains(s, na=False)
                ]

            # Create columns configuration
            columns = []
            for col in df.columns:
                if col == "Image":
                    columns.append({"name": col, "id": col, "presentation": "markdown"})
                else:
                    columns.append({"name": col, "id": col})
            
            return df.to_dict('records'), columns
            
        except Exception as e:
            print("Error in update_table:", e)
            import traceback
            traceback.print_exc()
            return [], DEFAULT_COLUMNS

    @app.callback(
        Output("map-markers", "children"),
        Input('mqtt-store', 'data')
    )
    def update_map_markers(mqtt_store_data):
        if not mqtt_store_data:
            return []

        markers = []
        for entry in mqtt_store_data:
            gps_str = entry.get("GPS", "")
            lat, lon = parse_gps(gps_str)
            if lat is not None and lon is not None:
                address = entry.get("Address", "N/A")
                image_url = entry.get("ImageURL", "")
                popup_children = [
                    html.B(f"ID: {entry.get('ID', 'N/A')}"),
                    html.Br(),
                    html.Span(f"Address: {address}")
                ]
                
                # popup image when click on the pin
                if image_url:
                    popup_children.extend([
                        html.Br(),
                        html.Img(src=image_url, style={"width": "150px", "marginTop": "5px", "borderRadius": "8px"})
                    ])
                markers.append(dl.Marker(position=[lat, lon], children=[dl.Popup(popup_children)]))
        return markers