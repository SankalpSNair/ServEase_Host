import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
import time

def test_add_house_maid():
    """Test adding a new house maid functionality"""
    print("\n=== Starting Add House Maid Test ===")
    
    driver = webdriver.Chrome()
    try:
        # Maximize window to avoid responsive menu issues
        driver.maximize_window()
        
        # First login
        print("Step 1: Logging in...")
        driver.get("http://127.0.0.1:8000/login/")
        
        # Login with credentials
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys("admin@gmail.com")
        
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password_field.send_keys("Admin@1234")
        
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "signin"))
        )
        login_button.click()
        print("Logged in successfully")

        # Wait for dashboard to load
        time.sleep(2)

        # Navigate to Manage Workers dropdown
        print("\nStep 2: Navigating to Manage Workers...")
        
        # Click Manage Workers using JavaScript
        manage_workers = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(.,'Manage Workers')]"))
        )
        driver.execute_script("arguments[0].click();", manage_workers)
        time.sleep(1)

        # Click House Maid option using JavaScript
        house_maid_option = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(.,'House Maid')]"))
        )
        driver.execute_script("arguments[0].click();", house_maid_option)
        print("Navigated to House Maid management page")

        # Wait for the page to load and verify we're on the correct page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(),'House Maid')]"))
        )

        # Click on Add House Maid button
        add_maid_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Add House Maid')]"))
        )
        driver.execute_script("arguments[0].click();", add_maid_button)
        print("Clicked on Add House Maid button")

        # Debug: Print current URL
        print(f"Current URL: {driver.current_url}")

        # Wait for form to load
        time.sleep(2)

        # Fill the form
        print("\nStep 3: Filling house maid form...")
        
        try:
            # Personal Details
            first_name = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    "input[name='firstname'], input[name='first_name'], #firstname, #first_name"
                ))
            )
            first_name.send_keys("Jane")
            print("Found and filled first name field")

            last_name = driver.find_element(By.CSS_SELECTOR, 
                "input[name='lastname'], input[name='last_name'], #lastname, #last_name")
            last_name.send_keys("Thomas")

            email = driver.find_element(By.CSS_SELECTOR, "input[name='email'], #email")
            email.send_keys("janethoms@gmail.com")

            phone = driver.find_element(By.CSS_SELECTOR, "input[name='phone'], #phone")
            phone.send_keys("7025417191")

            # Location Details
            district = driver.find_element(By.CSS_SELECTOR, 
                "input[name='district'], #district, select[name='district']")
            if district.tag_name == 'select':
                Select(district).select_by_visible_text("Ernakulam")  # Adjust district name as needed
            else:
                district.send_keys("Ernakulam")

            place = driver.find_element(By.CSS_SELECTOR, "input[name='place'], #place")
            place.send_keys("Kakkanad")

            address = driver.find_element(By.CSS_SELECTOR, 
                "input[name='address'], #address, textarea[name='address']")
            address.send_keys("MTRA 94, Kakkanad")

            # Professional Details
            experience = driver.find_element(By.CSS_SELECTOR, "input[name='experience'], #experience")
            experience.send_keys("5")

            # Try to find availability dropdown
            try:
                availability = Select(driver.find_element(By.CSS_SELECTOR, 
                    "select[name='availability'], #availability"))
                availability.select_by_value("true")
            except:
                print("Availability dropdown not found or not selectable")

            # Submit the form
            print("\nStep 4: Submitting the form...")
            submit_button = driver.find_element(By.CSS_SELECTOR,
                "button[type='submit'], input[type='submit'], #submit, .submit-btn")
            driver.execute_script("arguments[0].click();", submit_button)

            # Wait for success message or redirect with multiple possible success indicators
            try:
                # Wait for either success message or redirect
                success = False
                timeout = time.time() + 10  # 10 seconds timeout

                while time.time() < timeout and not success:
                    try:
                        # Check for success message
                        success_elements = driver.find_elements(By.CSS_SELECTOR, 
                            ".alert-success, .success-message, #success-message")
                        
                        # Check for redirect to house maid list
                        current_url = driver.current_url
                        if (len(success_elements) > 0 or 
                            "manage_house_maids" in current_url or 
                            "success" in current_url.lower()):
                            success = True
                            break
                        
                        time.sleep(0.5)
                    except:
                        time.sleep(0.5)

                if success:
                    print("\n✅ ADD HOUSE MAID TEST PASSED!")
                    print("=====================================")
                    print("✓ Successfully logged in")
                    print("✓ Navigated to house maid page")
                    print("✓ Filled and submitted the form")
                    print("✓ Form submission successful")
                    print("=====================================")
                else:
                    print("\n❌ ADD HOUSE MAID TEST FAILED!")
                    print("=====================================")
                    print("✗ Form submission status unclear")
                    print(f"Current URL: {driver.current_url}")
                    print("Page source after submission:")
                    print(driver.page_source)
                    print("=====================================")
                    raise TimeoutException("Could not verify successful form submission")

            except Exception as e:
                print("\n❌ ADD HOUSE MAID TEST FAILED!")
                print("=====================================")
                print(f"✗ Error during form submission: {str(e)}")
                print(f"Current URL: {driver.current_url}")
                
                # Print any error messages that might be on the page
                error_messages = driver.find_elements(By.CSS_SELECTOR, 
                    ".alert-danger, .error-message, .invalid-feedback")
                if error_messages:
                    print("\nError messages found on page:")
                    for error in error_messages:
                        print(f"- {error.text}")
                
                print("\nForm field values:")
                form_fields = driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
                for field in form_fields:
                    field_id = field.get_attribute('id')
                    field_name = field.get_attribute('name')
                    field_value = field.get_attribute('value')
                    print(f"Field {field_id or field_name}: {field_value}")
                
                print("=====================================")
                raise

        except Exception as e:
            print(f"Error while filling form: {str(e)}")
            print("\nAvailable elements on page:")
            form_elements = driver.find_elements(By.TAG_NAME, "input")
            for element in form_elements:
                print(f"Input element - ID: {element.get_attribute('id')}, "
                      f"Name: {element.get_attribute('name')}, "
                      f"Type: {element.get_attribute('type')}")
            print("\nPage source:")
            print(driver.page_source)
            raise

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        raise
        
    finally:
        print("\nClosing browser...")
        driver.quit()
        print("Test completed")

if __name__ == "__main__":
    test_add_house_maid()