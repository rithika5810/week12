
import pytest
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


APP_ROOT = Path(__file__).resolve().parents[1]
APP_URL = "http://127.0.0.1:5000/"


@pytest.fixture(scope="session")
def app_server():
    try:
        with urllib.request.urlopen(APP_URL, timeout=1) as response:
            if response.status == 200:
                yield
                return
    except (urllib.error.URLError, TimeoutError):
        pass

    process = subprocess.Popen(
        [sys.executable, str(APP_ROOT / "app.py")],
        cwd=APP_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output, _ = process.communicate()
            pytest.fail(f"Flask app exited before it was ready:\n{output}")
        try:
            with urllib.request.urlopen(APP_URL, timeout=1) as response:
                if response.status == 200:
                    break
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.25)
    else:
        process.terminate()
        output, _ = process.communicate()
        pytest.fail(f"Flask app did not start within 15 seconds:\n{output}")

    try:
        yield
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


# Fixture for setting up and tearing down the driver
@pytest.fixture
def setup_teardown(app_server):
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )
    driver.maximize_window()
    yield driver
    driver.quit()


# Test 1: Registration page loads correctly
def test_registration_page(setup_teardown):
    driver = setup_teardown
    driver.get("http://127.0.0.1:5000/")

    assert driver.title == "Registration Form"
    assert driver.find_element(By.TAG_NAME, "h2").text == \
        "Student Registration Form"


# Test 2: Name field is available
def test_registration_fields(setup_teardown):
    driver = setup_teardown
    driver.get("http://127.0.0.1:5000/")

    assert driver.find_element(By.NAME, "name").is_displayed()
    assert driver.find_element(By.NAME, "email").is_displayed()
    assert driver.find_element(By.NAME, "phone").is_displayed()
    assert driver.find_element(By.NAME, "course").is_displayed()


# Test 3: Course can be selected
def test_course_selection(setup_teardown):
    driver = setup_teardown
    driver.get("http://127.0.0.1:5000/")

    course = Select(driver.find_element(By.NAME, "course"))
    course.select_by_visible_text("B.Tech")

    assert course.first_selected_option.text == "B.Tech"


# Test 4: Successful registration
def test_valid_registration(setup_teardown):
    driver = setup_teardown
    driver.get("http://127.0.0.1:5000/")

    driver.find_element(By.NAME, "name").send_keys("Rithika")
    driver.find_element(By.NAME, "email").send_keys(
        "rithikajalagam24@gmail.com"
    )
    driver.find_element(By.NAME, "phone").send_keys("9876543210")

    Select(
        driver.find_element(By.NAME, "course")
    ).select_by_visible_text("B.Tech")

    driver.find_element(
        By.XPATH, "//button[@type='submit']"
    ).click()

    message = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.TAG_NAME, "h3"))
    ).text

    assert message == "Registration successful! Welcome, Rithika."
