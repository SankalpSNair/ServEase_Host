from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import easygui

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@(gmail\.com|yahoo\.com|[a-zA-Z0-9.-]+\.in)$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

driver = webdriver.Chrome()

try:
    # Login process (unchanged)
    driver.get("http://127.0.0.1:8000/login/")
    print("Opened the login page.")
    driver.maximize_window()
    time.sleep(3)

    wait = WebDriverWait(driver, 10)
    username_field = wait.until(EC.visibility_of_element_located((By.ID, "username")))
    username_field.clear()
    username_field.send_keys('sankalpsnair01@gmail.com')
    print("Entered username.")
    time.sleep(1)

    password_field = wait.until(EC.visibility_of_element_located((By.ID, 'password')))
    password_field.clear()
    password_field.send_keys('Sankalp@123')
    print("Entered password.")
    time.sleep(1)

    login_button = wait.until(EC.element_to_be_clickable((By.ID, 'signin')))
    print("Login button found. Clicking the button.")
    login_button.click()
    time.sleep(3)

    WebDriverWait(driver, 10).until(lambda d: "index" in d.current_url)
    if "index" in driver.current_url:
        print("Login successful. Redirected to index page.")
    else:
        raise Exception(f"Login failed. Current URL: {driver.current_url}")

    # Navigate to the profile page
    driver.get("http://127.0.0.1:8000/profile/")
    print("Navigated to the profile page.")
    time.sleep(3)

    # Click on the Edit Profile button
    edit_button = wait.until(EC.element_to_be_clickable((By.ID, 'edit-profile-btn')))
    edit_button.click()
    print("Clicked Edit Profile button.")
    time.sleep(2)

    # Update First Name
    first_name_field = wait.until(EC.visibility_of_element_located((By.ID, 'first-name')))
    first_name_field.clear()
    first_name_field.send_keys('Sankalp')
    print("Updated First Name.")

    # Update Last Name
    last_name_field = wait.until(EC.visibility_of_element_located((By.ID, 'last-name')))
    last_name_field.clear()
    last_name_field.send_keys('S')
    print("Updated Last Name.")

    # Update Phone
    phone_field = wait.until(EC.visibility_of_element_located((By.ID, 'phone')))
    phone = '9846893165'
    phone_field.clear()
    phone_field.send_keys(phone)
    print("Updated Phone Number.")

    if not validate_phone(phone):
        raise ValueError("Invalid phone number format. Must be a 10-digit number starting with 6, 7, 8, or 9.")

    # Update Address
    address_field = wait.until(EC.visibility_of_element_located((By.ID, 'address')))
    address_field.clear()
    address_field.send_keys('Thekkeplackal house, Vadakkekara P.O, Thrissur, Kerala, India')
    print("Updated Address.")

    # Upload profile picture (if available)
    try:
        profile_pic_input = wait.until(EC.presence_of_element_located((By.ID, 'profile-pic-input')))
        profile_pic_path = r"C:\path\to\your\picture.jpg"  # Update this path
        profile_pic_input.send_keys(profile_pic_path)
        print("Uploaded profile picture.")
    except Exception as e:
        print(f"Could not upload profile picture: {e}")

    # Click Save Changes button
    save_button = wait.until(EC.element_to_be_clickable((By.ID, 'save-profile-btn')))
    save_button.click()
    print("Clicked Save Changes button.")
    time.sleep(3)

    # Verify changes (optional)
    # You can add code here to check if the changes were applied successfully

    print("Profile update complete.")
    easygui.msgbox("Profile updated successfully", title="Success")

except Exception as e:
    print(f"An error occurred: {e}")
    easygui.msgbox(f"An error occurred: {e}", title="Error")

finally:
    time.sleep(3)
    driver.quit()


