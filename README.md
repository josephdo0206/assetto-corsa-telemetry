# Assetto Corsa Live Telemetry Extractor: Real-Time UDP Data Pipeline

## Project Overview
This project is a custom Python-based telemetry extraction tool designed to interface with the Assetto Corsa simulation environment. It streams live UDP packet data, extracts real-time vehicle performance metrics, and triggers automated alerts for mechanical threshold events (e.g., extreme over-revving during aggressive downshifts) for QA and system validation.

**Current Status:** Work in Progress (Formatted CSV logging and formal QA test cases are actively in development).

## Tech Stack
* **Language:** Python 3.x
* **Core Libraries:** Socket, Struct
* **Environment:** Assetto Corsa (PC)
* **Data Protocol:** UDP (User Datagram Protocol)

## The Methodology
**1. Live UDP Packet Extraction (Python/Socket)**
* Configured a continuous network socket connection to capture live UDP telemetry data streaming directly from the application environment.
* Handled real-time data ingestion to maintain a stable stream during continuous high-frequency transmission.

**2. Real-Time Telemetry Parsing (Struct)**
* Utilized the **Struct** library to unpack binary payload data into a readable, structured format.
* Isolated and tracked specific vehicle parameters required for QA validation, including RPM, current speed, and gear selection.

**3. Threshold Monitoring & Automated Alerting**
* Engineered logic to monitor mechanical thresholds in real-time, actively checking for parameters operating outside of standard tolerances.
* Validated the monitoring system by executing aggressive downshift scenarios in test vehicles (Mitsubishi Lancer Evolution VIII, Honda NSX) to successfully trigger automated over-rev alerts.
