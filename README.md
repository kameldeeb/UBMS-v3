# UBMS (Unified Behavior Monitoring System)

UBMS is a unified monitoring system that collects, stores, and displays various events and logs from different sources such as device activities, login attempts, and network usage. It also performs anomaly detection using an Isolation Forest model. The application leverages Streamlit to provide an interactive dashboard and analysis views.

## Installation and Running the Project

1. **Install the Required Packages**

   All required libraries are listed in the `requirements.txt` file. Install them using:

  
   pip install -r requirements.txt
  

2. **Run the Project**

   The project is started using Streamlit. Run the main file with the following command:

  
   streamlit run main.py
  

## Features

- **Dashboard Overview**  
  Displays key metrics including total devices, total events, alerts, and detected anomalies. Visualizations include:
  - Events by Category (bar chart)
  - Events Over Time (line chart)
  - Latest 10 Events with JSON-formatted details

- **Login Monitoring**  
  Tracks real-time login attempts with metrics for:
  - Total Attempts
  - Successful Logins
  - Failed Attempts  
  Also displays a detailed history of login attempts.

- **Anomaly Analysis**  
  Performs anomaly detection on the unified events data using an Isolation Forest model and displays:
  - Anomaly Summary per Device
  - Time series chart for anomalies
  - Detailed anomaly events with expanded JSON details

- **Unified Database**  
  Uses a single SQLite database (`data/database.db`) to store data across various modules:
  - Devices
  - Events
  - Alerts
  - Login Attempts
  - Network Logs

## Project Structure
├── app/
│   ├── components/
│   │   └── sidebar.py                 # Sidebar components for the UI
│   ├── core/
│   │   └── constants.py               # Application constants
│   ├── services/
│   │   ├── db_manager.py              # Database connection and CRUD functions
│   │   ├── device_manager_service.py  # Device manager service for device operations
│   │   ├── device_service.py          # Device-related monitoring operations
│   │   ├── file_service.py            # File monitoring operations
│   │   ├── login_service.py           # Login monitoring service (with threaded login tracking)
│   │   ├── network_service.py         # Network monitoring and traffic analysis
│   │   ├── process_service.py         # Process-related activities and monitoring
│   │   └── usb_service.py             # USB event tracking and management
│   ├── utils/
│   │   ├── anomaly_detection.py       # Anomaly detection for suspicious activities
│   │   ├── devices.py                 # Device management utilities
│   │   ├── logger.py                  # Logger utility for system events
│   │   ├── state.py                   # Session state and management utilities
│   ├── views/
│   │   ├── alerts_view.py             # Alerts view for displaying system alerts
│   │   ├── analysis_view.py           # Anomaly analysis view for monitoring and analyzing detected anomalies
│   │   ├── dashboard.py               # Main dashboard view for displaying system metrics and navigation
│   │   ├── devices_view.py            # Devices view for managing connected devices
│   │   ├── file_view.py               # File activities view for tracking file-related events
│   │   ├── login_view.py              # Login monitoring view for tracking user logins
│   │   ├── network_view.py            # Network activities view for monitoring network traffic
│   │   ├── process_view.py            # Process activities view for monitoring running processes
│   │   ├── settings_view.py           # Application settings view for managing configurations
│   │   └── usb_view.py                # USB events view for tracking USB device actions
├── data/
│   └── database.db                    # SQLite database file (automatically created)
├── main.py                            # Main entry point for the project (handles app initialization and layout)
├── run.py                             # Main entry point for launching the application (starts the app and runs it in a browser)
├── requirements.txt                   # Python dependencies for the application
└── README.md                          # Project documentation file with setup instructions and details
