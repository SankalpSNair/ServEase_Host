import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def test_successful_login():
    """Test successful login with valid credentials"""
    print("\n=== Starting Login Test ===")
    driver = webdriver.Chrome()
    try:
        # Navigate to login page
        print("Navigating to login page...")
        driver.get("http://127.0.0.1:8000/login/")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Page loaded successfully")
        
        # Print current URL for debugging
        print(f"Current URL: {driver.current_url}")
        
        # Print attempt message
        print("\nAttempting login with provided credentials...")
        
        # Wait for username field to be present
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys("sankalpsnair01@gmail.com")
        print("Username entered")
        
        # Wait for password field
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password_field.send_keys("Sankalp@123")
        print("Password entered")
        
        # Wait for login button
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "signin"))
        )
        print("Clicking login button...")
        login_button.click()
        
        try:
            # Wait for URL change
            print("Waiting for URL change...")
            WebDriverWait(driver, 10).until(
                EC.url_changes("http://127.0.0.1:8000/login/")
            )
            
            # Check if redirected to the correct index page
            expected_url = "http://127.0.0.1:8000/index/"
            print(f"\nChecking redirect URL...")
            print(f"Current URL: {driver.current_url}")
            print(f"Expected URL: {expected_url}")
            
            if driver.current_url == expected_url:
                print("\n✅ LOGIN TEST PASSED!")
                print("=====================================")
                print("✓ Login Successful")
                print("✓ Correctly redirected to index page")
                print("=====================================")
            else:
                print("\n❌ LOGIN TEST FAILED!")
                print("=====================================")
                print("✗ Redirect to wrong URL")
                print(f"Expected: {expected_url}")
                print(f"Got: {driver.current_url}")
                print("=====================================")
                raise AssertionError("Redirect to incorrect URL")
                
        except TimeoutException:
            print("\n❌ LOGIN TEST FAILED!")
            print("=====================================")
            print("✗ No redirect occurred")
            print("✗ Possible invalid credentials")
            print("=====================================")
            raise
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        raise
        
    finally:
        print("\nClosing browser...")
        driver.quit()
        print("Test completed")