from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
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
    
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

def setup_driver():
    """Setup Chrome with Windows-specific stable options"""
    chrome_options = Options()
    
    # Essential headless options
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # GPU and graphics options (fixes the GPU errors)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-gpu-sandbox")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-3d-apis")
    chrome_options.add_argument("--disable-accelerated-2d-canvas")
    chrome_options.add_argument("--disable-accelerated-jpeg-decoding")
    chrome_options.add_argument("--disable-accelerated-mjpeg-decode")
    chrome_options.add_argument("--disable-accelerated-video-decode")
    
    # Network and proxy options (fixes proxy resolver errors)
    chrome_options.add_argument("--no-proxy-server")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-sync")
    
    # Remove problematic single-process mode
    # chrome_options.add_argument("--single-process")  # This causes issues on Windows
    
    # Additional stability options
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    
    # Memory options
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--max_old_space_size=2048")
    
    # Window size
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Additional Windows-specific options
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--silent")
    chrome_options.add_argument("--log-level=3")
    
    # Prefs to disable more features
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.media_stream": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        print("✅ Chrome driver created successfully")
        return driver
    except Exception as e:
        print(f"❌ Failed to create driver: {e}")
        return None

def login_to_mcserverhost(driver, username, password):
    try:
        print("Logging in...")
        driver.get("https://www.mcserverhost.com/login")
        
        username_field = WebDriverWait(driver, 15).until(
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
    """Check server status with better error handling"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            print(f"Checking server status (attempt {attempt + 1}/{max_retries})...")
            
            driver.get("https://www.mcserverhost.com/servers/e9750610/dashboard")
            time.sleep(5)  
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if server is paused/suspended
            try:
                suspended_card = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "suspended-card"))
                )
                if suspended_card.is_displayed():
                    print("⏸️ Server is PAUSED! Resuming server...")
                    
                    resume_button = driver.find_element(By.CSS_SELECTOR, "button.btn-solid.theme-blue")
                    resume_button.click()
                    
                    print("✅ Resume button clicked! Waiting for resume...")
                    time.sleep(15)  
                    
                    # Refresh and check status after resume
                    driver.refresh()
                    time.sleep(5)
                    
                    # Check status after resume
                    status_div = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.ID, "status-buttons"))
                    )
                    
                    status = status_div.get_attribute("status")
                    print(f"Status after resume: {status}")
                    
                    if status == "offline":
                        print("🔴 Server offline after resume! Starting...")
                        start_button = driver.find_element(By.CSS_SELECTOR, "button.power-btn.start")
                        start_button.click()
                        print("✅ Start button clicked!")
                        return f"Server resumed and started at {current_time}"
                    else:
                        return f"Server resumed, status: {status} at {current_time}"
                        
            except TimeoutException:
                # No suspended card, check normal status
                pass
            
            # Check normal server status
            status_div = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "status-buttons"))
            )
            
            status = status_div.get_attribute("status")
            print(f"[{current_time}] Server status: {status}")
            
            if status == "offline":
                print("🔴 Server is offline! Starting server...")
                start_button = driver.find_element(By.CSS_SELECTOR, "button.power-btn.start")
                start_button.click()
                print("✅ Start button clicked!")
                return f"Server started at {current_time}"
            else:
                return f"Server is {status} at {current_time}"
                
        except WebDriverException as e:
            print(f"WebDriver error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("Retrying in 10 seconds...")
                time.sleep(10)
                continue
            else:
                return f"WebDriver crashed after {max_retries} attempts"
                
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("Retrying in 10 seconds...")
                time.sleep(10)
                continue
            else:
                return f"Error after {max_retries} attempts: {str(e)}"
    
    return "Failed to check server status"

def monitor_server_thread(username, password, check_interval, http_server):
    print("🎮 MCServer Auto-Start Monitor")
    print("=" * 40)
    print(f"Check interval: {check_interval//60} minutes")
    print("=" * 40)
    
    driver = None
    consecutive_failures = 0
    max_failures = 3
    
    try:
        while True:
            try:
                # Create new driver if needed or if there were failures
                if driver is None or consecutive_failures >= 2:
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                    
                    print("Creating new browser instance...")
                    driver = setup_driver()
                    
                    if not driver:
                        consecutive_failures += 1
                        http_server.status_info = f"Failed to create browser ({consecutive_failures}/{max_failures})"
                        time.sleep(60)
                        continue
                    
                    if not login_to_mcserverhost(driver, username, password):
                        consecutive_failures += 1
                        http_server.status_info = f"Login failed ({consecutive_failures}/{max_failures})"
                        time.sleep(60)
                        continue
                
                # Check server status
                status_result = check_and_start_server(driver)
                http_server.status_info = status_result
                consecutive_failures = 0  # Reset on success
                
                print(f"⏳ Next check in {check_interval//60} minutes...")
                time.sleep(check_interval)
                
            except Exception as e:
                consecutive_failures += 1
                error_msg = f"Monitor error ({consecutive_failures}/{max_failures}): {str(e)}"
                http_server.status_info = error_msg
                print(f"❌ {error_msg}")
                
                if consecutive_failures >= max_failures:
                    print("Too many failures, restarting completely...")
                    consecutive_failures = 0
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                        driver = None
                
                time.sleep(60)
                
    except Exception as e:
        print(f"Monitor thread fatal error: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    USERNAME = "YOUR_USERNAME"
    PASSWORD = "YOUR_PASSWORD"
    CHECK_INTERVAL = 60  # 1 minute

    PORT = int(os.environ.get('PORT', 10000))
    
    http_server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    http_server.status_info = "Starting up..."
    
    print(f"🌐 HTTP server starting on port {PORT}")
    
    monitor_thread = threading.Thread(
        target=monitor_server_thread, 
        args=(USERNAME, PASSWORD, CHECK_INTERVAL, http_server),
        daemon=True
    )
    monitor_thread.start()
    
    try:
        print("🚀 Server running!")
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        http_server.shutdown()

if __name__ == "__main__":
    main()