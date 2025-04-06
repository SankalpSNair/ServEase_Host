import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import time
from pathlib import Path

def test_download_invoice():
    """Test downloading invoice for electrician booking"""
    print("\n=== Starting Invoice Download Test ===")
    
    driver = webdriver.Chrome()
    try:
        # Maximize window to avoid responsive menu issues
        driver.maximize_window()
        
        # Navigate to login page
        print("Navigating to login page...")
        driver.get("http://127.0.0.1:8000/login/")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Page loaded successfully")
        
        # Login process
        print("\nAttempting login with provided credentials...")
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys("sankalpsnair01@gmail.com")
        
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password_field.send_keys("Sankalp@123")
        
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "signin"))
        )
        login_button.click()
        print("Login credentials submitted")

        # Wait for dashboard to load
        time.sleep(2)
        print("Waiting for dashboard to load...")

        try:
            # Try to find and click the sidebar toggle if it exists
            try:
                sidebar_toggle = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sidebar-hide"))
                )
                sidebar_toggle.click()
                time.sleep(1)
            except:
                print("No sidebar toggle found or not needed")

            # Navigate to Bookings using different possible selectors
            print("\nLocating Bookings link...")
            bookings_xpath_options = [
                "//a[contains(text(),'Bookings')]",
                "//a[contains(.,'Bookings')]",
                "//span[contains(text(),'Bookings')]/..",
                "//div[contains(@class,'sidebar')]//a[contains(.,'Bookings')]"
            ]

            bookings_link = None
            for xpath in bookings_xpath_options:
                try:
                    bookings_link = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    break
                except:
                    continue

            if bookings_link:
                print("Found Bookings link")
                # Try different click methods
                try:
                    bookings_link.click()
                except:
                    try:
                        driver.execute_script("arguments[0].click();", bookings_link)
                    except:
                        driver.get(bookings_link.get_attribute('href'))
                
                time.sleep(2)
                print("Clicked Bookings link")

                # Look for the first electrician booking's download button
                print("\nLocating download button for electrician booking...")
                download_selectors = [
                    "a[href*='download_invoice']",
                    ".download-invoice",
                    ".download-btn",
                    "button[onclick*='download']",
                    "a[onclick*='download']",
                    "//tr[contains(.,'Electrician')]//a[contains(@href,'download')]"  # XPath for finding download in electrician row
                ]

                download_button = None
                for selector in download_selectors:
                    try:
                        if '//' in selector:  # XPath selector
                            download_button = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:  # CSS selector
                            download_button = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        break
                    except:
                        continue

                if download_button:
                    print("Found download button")
                    # Get the expected filename if possible
                    try:
                        href = download_button.get_attribute('href')
                        print(f"Download URL: {href}")
                    except:
                        print("Could not get download URL")

                    # Click the download button
                    driver.execute_script("arguments[0].click();", download_button)
                    print("Clicked download button")
                    time.sleep(5)  # Wait for download to start
                    print("\n✅ INVOICE DOWNLOAD TEST PASSED!")
                else:
                    print("\n❌ Download button not found!")
                    print(f"Current URL: {driver.current_url}")
                    print("Page source:")
                    print(driver.page_source[:1000])
            else:
                print("\n❌ Bookings link not found!")
                print(f"Current URL: {driver.current_url}")
                print("Available links:")
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    print(f"Link text: {link.text}, href: {link.get_attribute('href')}")

        except Exception as e:
            print(f"\n❌ Error during navigation: {str(e)}")
            print(f"Current URL: {driver.current_url}")
            print("Page source:")
            print(driver.page_source[:1000])
            raise

    finally:
        print("\nClosing browser...")
        driver.quit()
        print("Test completed")

if __name__ == "__main__":
    test_download_invoice()
