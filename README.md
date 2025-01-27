# PoE2 Map Tracker

A PyQt6-based application for tracking Path of Exile 2 map runs, including time spent, boss kills, and loot obtained.

## Project Structure

```
atlas-archive/
├── src/
│   ├── dialogs/           # UI dialog components
│   │   ├── __init__.py
│   │   ├── boss_kill_dialog.py
│   │   ├── item_entry_dialog.py
│   │   ├── map_completion_dialog.py
│   │   ├── map_run_details_dialog.py
│   │   └── map_runs_dialog.py
│   └── utils/             # Utility modules
│       ├── __init__.py
│       ├── database.py    # SQLite database handling
│       ├── item_parser.py # Item clipboard parsing
│       └── log_parser.py  # Client.txt log parsing
├── main.py               # Application entry point
├── settings.json        # User settings
└── README.md
```

## Features

- Track map run duration
- Record boss kills
- Log items found (via clipboard)
- View run history
- Export data to CSV
- Dark mode UI

## Requirements

- Python 3.x
- PyQt6

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install PyQt6
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Click "Select Client.txt" to choose your Path of Exile 2 Client.txt file
3. Click "Start Monitoring" to begin tracking map runs
4. Use "End Map" when you want to manually end a map run
5. Use "Log Items" to record items from your clipboard
6. View your run history with the "View Runs" button

## Database

The application uses SQLite to store map run data in `poe2_maps.db`. This includes:
- Map name
- Start time
- Duration
- Boss kill status
- Items found
- Completion status (Complete/RIP)
