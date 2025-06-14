from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        status_info = getattr(self.server, 'status_info', 'Monitor starting...')
        
        response = f"""
        <html>
        <head><title>MCServer Monitor</title></head>
        <body>
            <h1>🎮 MCServer Auto-Start Monitor</h1>
            <p><strong>Status:</strong> {status_info}</p>
            <p><strong>Last Check:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>Monitor is running successfully!</p>
        </body>
        </html>
        """
        self.wfile.write(response.encode())

def setup_driver():
    """Setup headless Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    return webdriver.Chrome(options=chrome_options)

def login_to_mcserverhost(driver, username, password):
    """Login to MCServerHost"""
    try:
        print("Logging in...")
        driver.get("https://www.mcserverhost.com/login")
        
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "auth-username"))
        )
        username_field.clear()
        username_field.send_keys(username)
        
        password_field = driver.find_element(By.ID, "auth-password")
        password_field.clear()
        password_field.send_keys(password)
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[action='login']")
        login_button.click()
        
        time.sleep(5)
        
        if "login" not in driver.current_url:
            print("✅ Login successful!")
            return True
        else:
            print("❌ Login failed")
            return False
            
    except Exception as e:
        print(f"Login error: {e}")
        return False

def check_and_start_server(driver):
    """Check server status and start if offline"""
    try:
        # Go to server dashboard
        driver.get("https://www.mcserverhost.com/servers/e9750610/dashboard")
        time.sleep(3)
        
        try:
            status_resume = status_div.find_element(By.XPATH, ".//button[normalize-space(text())='RESUME']")
            print("🔵 Server needs to be resumed")
            status_resume.click()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return f"Server was resumed at {current_time}"
        except:
            pass

        # Check if server is offline and needs starting
        try:
            start_button = driver.find_element(By.CSS_SELECTOR, "button.power-btn.start")
            print("🔴 Server is offline! Starting server...")
            start_button.click()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return f"Server was offline, started at {current_time}"
        except:
            pass
            
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"Server appears to be running - {current_time}"
                
        except Exception as e:
            print(f"Error checking server: {e}")
            return f"Error: {e}" 

def monitor_server_thread(username, password, check_interval, http_server):
    """Monitor server in background thread"""
    print("🎮 MCServer Auto-Start Monitor")
    print("=" * 40)
    print(f"Check interval: {check_interval//60} minutes")
    print("=" * 40)
    
    driver = None
    
    try:
        while True:
            try:
                # Setup new driver if needed
                if driver is None:
                    driver = setup_driver()
                    
                    # Login
                    if not login_to_mcserverhost(driver, username, password):
                        http_server.status_info = "Login failed, retrying..."
                        print("❌ Login failed, retrying in 1 minute...")
                        if driver:
                            driver.quit()
                            driver = None
                        time.sleep(60)
                        continue
                
                # Check server status
                status_result = check_and_start_server(driver)
                http_server.status_info = status_result
                
                print(f"⏳ Next check in {check_interval//60} minutes...")
                
                # Wait for next check
                time.sleep(check_interval)
                
            except Exception as e:
                error_msg = f"Error in monitoring: {e}"
                http_server.status_info = error_msg
                print(f"❌ {error_msg}")
                print("Restarting in 1 minute...")
                
                if driver:
                    driver.quit()
                    driver = None
                
                time.sleep(60)
                
    except Exception as e:
        print(f"Monitor thread error: {e}")
    finally:
        if driver:
            driver.quit()

def main():
    # Configuration
    USERNAME = "Tofuism"
    PASSWORD = "8czgLVq52gDLGP9"
    CHECK_INTERVAL = 180  # 3 minutes in seconds
    
    # Get port from environment (Render provides this)
    PORT = int(os.environ.get('PORT', 10000))
    
    # Start HTTP server
    http_server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    http_server.status_info = "Starting up..."
    
    print(f"🌐 HTTP server starting on port {PORT}")
    print(f"🔗 Health check available at: http://localhost:{PORT}")
    
    # Start monitoring in background thread
    monitor_thread = threading.Thread(
        target=monitor_server_thread, 
        args=(USERNAME, PASSWORD, CHECK_INTERVAL, http_server),
        daemon=True
    )
    monitor_thread.start()
    
    # Start HTTP server (this blocks)
    try:
        print("🚀 Server running! Press Ctrl+C to stop")
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        http_server.shutdown()

if __name__ == "__main__":
    main()