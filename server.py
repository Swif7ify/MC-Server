from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime

def setup_driver():
    """Setup headless Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
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
        driver.get("https://www.mcserverhost.com/servers/e9750610/dashboard")
        time.sleep(3)
        
        status_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "status-buttons"))
        )
        
        status = status_div.get_attribute("status")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[{current_time}] Server status: {status}")
        
        if status == "offline":
            print("🔴 Server is offline! Starting server...")
            
            start_button = driver.find_element(By.CSS_SELECTOR, "button.power-btn.start")
            start_button.click()
            
            print("✅ Start button clicked! Server is starting...")
            return True
        else:
            print(f"✅ Server is {status}")
            return True
            
    except Exception as e:
        print(f"Error checking server: {e}")
        return False

def monitor_server(username, password, check_interval=180): 
    """Monitor server indefinitely"""
    print("🎮 MCServer Auto-Start Monitor")
    print("=" * 40)
    print(f"Check interval: {check_interval//60} minutes")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    driver = None
    
    try:
        while True:
            try:
                if driver is None:
                    driver = setup_driver()
                    
                    # Login
                    if not login_to_mcserverhost(driver, username, password):
                        print("❌ Login failed, retrying in 1 minute...")
                        if driver:
                            driver.quit()
                            driver = None
                        time.sleep(60)
                        continue
                
                if check_and_start_server(driver):
                    print(f"⏳ Next check in {check_interval//60} minutes...")
                else:
                    print("❌ Check failed, will retry...")
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                print("Restarting in 1 minute...")
                
                if driver:
                    driver.quit()
                    driver = None
                
                time.sleep(60)
                
    except KeyboardInterrupt:
        print("\n🛑 Monitor stopped by user")
    finally:
        if driver:
            driver.quit()
            print("🧹 Browser closed")

# Configuration
USERNAME = "Tofuism"
PASSWORD = "8czgLVq52gDLGP9"
CHECK_INTERVAL = 180 

# Start monitoring
monitor_server(USERNAME, PASSWORD, CHECK_INTERVAL)