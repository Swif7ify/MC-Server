# MCServer Auto-Start Monitor

This project is a Python-based monitoring tool for automatically checking and starting a Minecraft server hosted on MCServerHost.com. It uses Selenium WebDriver to automate browser actions and includes a built-in HTTP health check server for status monitoring.

## Features

-   **Automated Login:** Logs into MCServerHost.com using provided credentials.
-   **Server Status Check:** Periodically checks if your Minecraft server is running, paused, or offline.
-   **Auto-Resume/Start:** Automatically resumes or starts the server if it is paused or offline.
-   **Health Check HTTP Server:** Exposes a simple web interface to view the current status and last check time.
-   **Robust Error Handling:** Handles browser crashes and login failures with retries and automatic recovery.

## Requirements

-   Python 3.7+
-   Google Chrome browser
-   ChromeDriver (compatible with your Chrome version)
-   The following Python packages (see `requirements.txt`):
    -   selenium

## Installation

1. **Clone the repository:**
    ```powershell
    git clone <repo-url>
    cd MC-Server
    ```
2. **Install dependencies:**
    ```powershell
    pip install -r requirements.txt
    ```

## Configuration

-   Edit `server.py` and set your MCServerHost.com username and password:
    ```python
    USERNAME = "YOUR_USERNAME"
    PASSWORD = "YOUR_PASSWORD"
    ```
-   Optionally, set the `PORT` environment variable to change the HTTP server port (default is 10000).

## Usage

Run the server monitor with:

```powershell
python server.py
```

-   The HTTP health check server will be available at `http://localhost:10000` (or your chosen port).
-   The monitor will check your server status every minute by default.

## Hosting

You can also host this monitor on a cloud server or a VPS to keep your Minecraft server monitored 24/7. Just make sure your cloud environment supports running Chrome and ChromeDriver (for example, a Windows or Linux VM with a desktop environment).  
If you want to access the health check page remotely, ensure the chosen port is open in your firewall and security group settings.


## Security Note

**Do not share your credentials or commit them to public repositories.**

## License

MIT License
