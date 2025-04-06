import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def test_successful_signup():
    """Test successful signup with valid credentials"""
    print("\n=== Starting Signup Test ===")
    driver = webdriver.Chrome()
    try:
        # Navigate to signup page
        print("Navigating to signup page...")
        driver.get("http://127.0.0.1:8000")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Page loaded successfully")
        
        # Print current URL for debugging
        print(f"Current URL: {driver.current_url}")
        
        # Print attempt message
        print("\nAttempting signup with provided credentials...")
        
        # Fill in the signup form
        # First Name
        fname_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "fname"))
        )
        fname_field.send_keys("Aleena")
        print("First name entered")
        
        # Last Name
        lname_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "lname"))
        )
        lname_field.send_keys("Ginu")
        print("Last name entered")
        
        # Email
        email_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "email"))
        )
        email_field.send_keys("aleena@gmail.com")
        print("Email entered")
        
        # Password
        password_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "password"))
        )
        password_field.send_keys("Aleena@123")
        print("Password entered")
        
        # Confirm Password
        re_pass_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "re_pass"))
        )
        re_pass_field.send_keys("Aleena@123")
        print("Confirm password entered")
        
        # Terms checkbox - using JavaScript to click
        try:
            terms_checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "agree-term"))
            )
            driver.execute_script("arguments[0].click();", terms_checkbox)
            print("Terms accepted")
        except Exception as e:
            print(f"Failed to click terms checkbox: {str(e)}")
            raise
        
        # Click Register button using JavaScript
        try:
            register_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "signup"))
            )
            driver.execute_script("arguments[0].click();", register_button)
            print("Clicking register button...")
        except Exception as e:
            print(f"Failed to click register button: {str(e)}")
            raise
        
        try:
            # Wait for URL change
            print("Waiting for URL change...")
            WebDriverWait(driver, 10).until(
                EC.url_changes("http://127.0.0.1:8000")
            )
            
            # Check if redirected to the login page
            expected_url = "http://127.0.0.1:8000/login/"
            print(f"\nChecking redirect URL...")
            print(f"Current URL: {driver.current_url}")
            print(f"Expected URL: {expected_url}")
            
            if driver.current_url == expected_url:
                print("\n✅ SIGNUP TEST PASSED!")
                print("=====================================")
                print("✓ Signup Successful")
                print("✓ Correctly redirected to login page")
                print("=====================================")
            else:
                print("\n❌ SIGNUP TEST FAILED!")
                print("=====================================")
                print("✗ Redirect to wrong URL")
                print(f"Expected: {expected_url}")
                print(f"Got: {driver.current_url}")
                print("=====================================")
                raise AssertionError("Redirect to incorrect URL")
                
        except TimeoutException:
            print("\n❌ SIGNUP TEST FAILED!")
            print("=====================================")
            print("✗ No redirect occurred")
            print("✗ Possible validation error or server issue")
            print("=====================================")
            raise
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        raise
        
    finally:
        print("\nClosing browser...")
        driver.quit()
        print("Test completed")
