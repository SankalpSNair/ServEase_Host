import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
import os
import time
from pathlib import Path

def test_report_generation():
    """Test report generation functionality"""
    print("\n=== Starting Report Generation Test ===")
    
    # Setup Chrome options for download
    chrome_options = webdriver.ChromeOptions()
    download_dir = str(Path.home() / "Downloads")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True  # Force PDF to download instead of opening in browser
    })
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        # First login
        print("Step 1: Logging in...")
        driver.get("http://127.0.0.1:8000/login/")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Login page loaded successfully")
        
        # Login with credentials
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys("admin@gmail.com")
        print("Username entered")
        
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password_field.send_keys("Admin@1234")
        print("Password entered")
        
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "signin"))
        )
        login_button.click()
        print("Login button clicked")
        
        # Wait for successful login and redirect to dashboard
        WebDriverWait(driver, 10).until(
            EC.url_to_be("http://127.0.0.1:8000/dashboard/")
        )
        print("Successfully logged in and reached dashboard")
        
        # Navigate to report generation page
        print("\nStep 2: Navigating to Report Generation page...")
        report_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Report Generation"))
        )
        report_link.click()
        print("Clicked on Report Generation link")
        
        # Wait for report page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "reportTabs"))
        )
        print("Report Generation page loaded")
        
        # Fill report generation form
        print("\nStep 3: Filling report generation form...")
        
        # The Users tab should be active by default, but let's make sure
        users_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "users-tab"))
        )
        users_tab.click()
        print("Users tab selected")
        
        # Select user type as customer
        user_type = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "userType"))
        )
        Select(user_type).select_by_value("customer")
        print("Selected customer user type")
        
        # Generate report
        print("\nStep 4: Generating report...")
        
        # Using JavaScript to call the generateReport function directly
        driver.execute_script("generateReport('users')")
        print("Generate report button clicked")
        
        try:
            # Wait for report generation
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "usersTable"))
            )
            
            # Wait for download button to appear (indicates successful generation)
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "downloadUsersBtn"))
            )
            
            print("\n✅ REPORT GENERATION TEST PASSED!")
            print("=====================================")
            print("✓ Successfully logged in")
            print("✓ Navigated to report page")
            print("✓ Generated users report")
            print("=====================================")
            
        except TimeoutException:
            print("\n❌ REPORT GENERATION TEST FAILED!")
            print("=====================================")
            print("✗ Report generation failed or timeout")
            print("=====================================")
            raise
            
        # After successful report generation, click download PDF button
        print("\nStep 5: Downloading PDF report...")
        
        # Delete existing file if it exists
        filename = "users_report.pdf"
        filepath = os.path.join(download_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Removed existing file: {filepath}")
        
        # Wait for the download button to be visible and clickable
        download_pdf_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "downloadUsersPDFBtn"))
        )
        
        # Ensure the element is in view
        driver.execute_script("arguments[0].scrollIntoView(true);", download_pdf_button)
        time.sleep(1)  # Small pause to ensure element is fully in view
        
        # Click using JavaScript
        driver.execute_script("arguments[0].click();", download_pdf_button)
        print("Download PDF button clicked")

        # Wait for download to complete
        print("Waiting for download to complete...")
        
        # Wait up to 30 seconds for the file to download
        timeout = time.time() + 30
        downloaded = False
        while time.time() < timeout:
            if os.path.exists(filepath):
                # Check if file is fully downloaded by trying to open it
                try:
                    with open(filepath, 'rb') as file:
                        # Try to read the file
                        file.read()
                        downloaded = True
                        print(f"File downloaded successfully: {filepath}")
                        break
                except (IOError, PermissionError):
                    # File is still being downloaded
                    pass
            time.sleep(1)
            
        if downloaded:
            print("\n✅ REPORT GENERATION AND DOWNLOAD TEST PASSED!")
            print("=====================================")
            print("✓ Successfully logged in")
            print("✓ Navigated to report page")
            print("✓ Generated users report")
            print("✓ Downloaded PDF report")
            print("=====================================")
        else:
            print("\n❌ DOWNLOAD TEST FAILED!")
            print("=====================================")
            print("✗ PDF download failed or timeout")
            print("=====================================")
            raise TimeoutException("Download timeout")

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        raise
        
    finally:
        print("\nClosing browser...")
        driver.quit()
        print("Test completed")

if __name__ == "__main__":
    test_report_generation()

    