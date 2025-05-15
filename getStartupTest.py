from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv
import os
import re

def setup_driver():
    """Configure and return a Chrome browser with Selenium."""
    options = Options()
    # Uncomment to run in headless mode (without UI)
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    
    # Using Chrome with webdriver manager
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

def accept_cookies(driver):
    """Accept cookies on the VivaTechnology site."""
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
            )
        ).click()
        print("✅ Cookiebot accepted")
    except Exception as e:
        print("❌ No Cookiebot visible:", e)

def select_filters(driver, hashtags=None, company_types=None):
    """Select specified filters on the partners page."""
    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-slot='trigger']"))
    )
    
    # Select hashtags
    if hashtags and len(hashtags) > 0:
        try:
            # Click on the hashtags dropdown menu
            hashtag_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//label[contains(text(), 'Hashtags')]]"))
            )
            hashtag_dropdown.click()
            print("Hashtag dropdown clicked")
            
            # Wait for the hashtag list to appear
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "[role='listbox']"))
            )
            
            # Select each requested hashtag
            for tag in hashtags:
                print(f"Looking for hashtag: {tag}")
                try:
                    # Look for elements with the exact text in their span
                    tag_element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, f"//li[@role='option']//span[text()='{tag}']//ancestor::li"))
                    )
                    tag_element.click()
                    print(f"Hashtag '{tag}' selected")
                    time.sleep(1)  # Add a delay to let the page react
                except Exception as e:
                    print(f"Hashtag '{tag}' not found: {e}")
            
            # Close the dropdown by clicking elsewhere
            driver.find_element(By.TAG_NAME, 'body').click()
            time.sleep(1)  # Wait for dropdown to close
            
        except Exception as e:
            print(f"Error selecting hashtags: {e}")
    
    # Select company types
    if company_types and len(company_types) > 0:
        try:
            # Click on the company types dropdown menu
            company_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//label[contains(text(), 'Type of company')]]"))
            )
            company_dropdown.click()
            print("Company type dropdown clicked")
            
            # Wait for the company types list to appear
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "[role='listbox']"))
            )
            
            # Select each requested company type
            for company_type in company_types:
                try:
                    # Using similar XPath strategy as with hashtags
                    type_element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, f"//li[@role='option']//span[contains(text(), '{company_type}')]//ancestor::li"))
                    )
                    type_element.click()
                    print(f"Company type '{company_type}' selected")
                    time.sleep(1)  # Add a delay to let the page react
                except Exception as e:
                    print(f"Company type '{company_type}' not found: {e}")
            
            # Close the dropdown by clicking elsewhere
            driver.find_element(By.TAG_NAME, 'body').click()
            time.sleep(1)  # Wait for dropdown to close
            
        except Exception as e:
            print(f"Error selecting company types: {e}")

def get_partner_description(driver, partner_url):
    """Visit partner detail page in a new tab and extract description."""
    try:
        # Open new tab
        driver.execute_script("window.open('');")
        # Switch to the new tab (it will be the last tab)
        driver.switch_to.window(driver.window_handles[-1])
        
        # Visit partner page in the new tab
        driver.get(partner_url)
        print(f"Visiting partner page in new tab: {partner_url}")
        
        # Wait for the description to load
        time.sleep(1)
        
        description = ""
        # Try to find the description using the provided selector
        try:
            description_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.my-4.text-xs.leading-relaxed"))
            )
            description = description_element.text.strip()
        except TimeoutException:
            # If not found, keep description as empty string
            print(f"No description found for partner: {partner_url}")
            pass
        
        # Extract development level
        development_level = ""
        try:
            # Try to find the development level information
            dev_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'development level')]/following-sibling::p"))
            )
            development_level = dev_element.text.strip()
            print(f"Development level: {development_level}")
        except:
            print("Development level not found")
        
        # Extract booth information
        hall = ""
        booth = ""
        try:
            # Try to get booth information using the example from paste.txt
            location_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'symbols') and contains(text(), 'distance')]/following-sibling::span"))
            )
            location_text = location_element.text.strip()
            
            # Parse hall and booth from location text (format: "hall1 Booth C27-012")
            location_match = re.match(r'hall(\d+)\s+Booth\s+([A-Z0-9\-]+)', location_text, re.IGNORECASE)
            if location_match:
                hall = f"Hall {location_match.group(1)}"
                booth = location_match.group(2)
                print(f"Hall: {hall}, Booth: {booth}")
        except:
            print("Booth information not found")
        
        # Extract country/from information
        country = ""
        try:
            country_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'symbols') and contains(text(), 'flag')]/following-sibling::span"))
            )
            country = country_element.text.strip()
            print(f"Country: {country}")
        except:
            print("Country information not found")
        
        # Extract date information
        date = ""
        try:
            date_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'block mt-1')]"))
            )
            date_text = date_element.text.strip()
            date = date_text.replace('(', '').replace(')', '')  # Remove parentheses
            print(f"Date: {date}")
        except:
            print("Date information not found")
            
        # Close the tab and switch back to the main tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
        return {
            "description": description,
            "development_level": development_level,
            "hall": hall,
            "booth": booth,
            "country": country,
            "date": date
        }
    except Exception as e:
        print(f"Error getting partner details: {e}")
        # Make sure to close the tab and go back to main window in case of error
        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return {
            "description": "",
            "development_level": "",
            "hall": "",
            "booth": "",
            "country": "",
            "date": ""
        }

def scroll_until_all_partners_loaded(driver, selector=".grid > div"):
    last_count = 0
    max_attempts = 20
    attempts = 0

    while attempts < max_attempts:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        current_count = len(elements)
        print(f"Current partner count: {current_count}")
        
        if current_count == last_count:
            print("All partners loaded.")
            break
        
        last_count = current_count
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        attempts += 1

def extract_partner_data(driver):
    """Extract data from partners displayed on the page."""
    partners = []
    
    # Wait for the grid to load based on the provided class
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 
                ".w-full.max-w-\\[1800px\\].mx-auto.text-center.grid"))
        )
        print("Partner grid loaded")
    except TimeoutException:
        print("Timeout waiting for partner grid to load")
    
    # Wait for any potential loading animations to complete
    time.sleep(3)
    
    # Based on the provided HTML, we need to target the card container divs
    # Using a more specific selector based on the HTML structure
    try:
        partner_elements = driver.find_elements(By.CSS_SELECTOR, 
            "div.flex.flex-col.relative.overflow-hidden.text-foreground.box-border.outline-none")
        
        print(f"Number of partners found: {len(partner_elements)}")
        
        for element in partner_elements:
            try:
                # Extract partner name - based on provided HTML
                try:
                    name_element = element.find_element(By.CSS_SELECTOR, "h3.text-purple.font-bold.uppercase a")
                    name = name_element.text.strip()
                    
                    # Extract URL
                    partner_url = name_element.get_attribute("href")
                except NoSuchElementException:
                    try:
                        # Alternative way to find the name
                        name = element.find_element(By.CSS_SELECTOR, "h3 a").text.strip()
                        partner_url = element.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("href")
                    except NoSuchElementException:
                        name = ""
                        partner_url = ""
                
                # Extract company type - based on the provided HTML
                try:
                    company_type = element.find_element(By.CSS_SELECTOR, 
                        "div.flex.flex-wrap span.font-bold.capitalize").text.strip()
                except NoSuchElementException:
                    company_type = ""
                
                # Extract hashtags
                hashtags = []
                try:
                    # Based on the HTML structure, hashtags are in the second div container
                    hashtag_elements = element.find_elements(By.CSS_SELECTOR, 
                        "div.my-4.flex.flex-wrap.gap-2 div.relative.max-w-fit.min-w-min span.flex-1")
                    
                    for tag in hashtag_elements:
                        tag_text = tag.text.strip()
                        if tag_text and not tag_text.startswith("#"):  # Skip the "#" element
                            hashtags.append(tag_text)
                except Exception as e:
                    print(f"Error extracting hashtags: {e}")
                
                # Check if this partner has the "Cybersecurity" tag
                if "Cybersecurity" in hashtags and name and partner_url:
                    # Get additional details from partner page
                    partner_details = get_partner_description(driver, partner_url)
                    description = partner_details["description"]
                    
                    # Check if the partner meets our criteria:
                    # 1. Has "Cybersecurity" tag AND
                    # 2. Either has "Artificial Intelligence" tag OR has AI-related keywords in description
                    has_ai_tag = "Artificial Intelligence" in hashtags
                    has_ai_keywords = any(keyword in description.lower() for keyword in ["ai", "artificial intelligence", "machine learning", "ml", "ia", "intelligence artificielle", "neural", "deep learning"])
                    
                    if has_ai_tag or has_ai_keywords:
                        partner_data = {
                            "name": name,
                            "description": description,
                            "tags": ", ".join(hashtags),
                            "development_level": partner_details["development_level"],
                            "hall": partner_details["hall"],
                            "booth": partner_details["booth"],
                            "date": partner_details["date"],
                            "from": partner_details["country"],
                            "url": partner_url
                        }
                        partners.append(partner_data)
                        print(f"Added matching partner: {name}")
                    else:
                        print(f"Skipped partner (no AI connection): {name}")
            except Exception as e:
                print(f"Error extracting data from a partner: {e}")
                continue
                
    except Exception as e:
        print(f"Error extracting partners: {e}")
    
    return partners

def save_to_csv(partners, filename="vivatech_cybersecurity_ai_partners.csv"):
    """Save partner data to a CSV file, appending V1, V2... if filename already exists."""

    if not partners:
        print("No partners to save")
        return

    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    # Check for existing file and increment counter if needed
    while os.path.exists(new_filename):
        new_filename = f"{base}_V{counter}{ext}"
        counter += 1

    try:
        with open(new_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["Nom", "Description", "Tag", "Development", "Hall", "Booth", "Jours", "Origine","Url"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for partner in partners:
                writer.writerow({
                    "Nom": partner["name"],
                    "Description": partner["description"],
                    "Tag": partner["tags"],
                    "Development": partner["development_level"],
                    "Hall": partner["hall"],
                    "Booth": partner["booth"],
                    "Jours": partner["date"],
                    "Origine": partner["from"],
                    "Url": partner["url"]
                })
            
        print(f"Data successfully saved to {new_filename}")
        print(f"Absolute path: {os.path.abspath(new_filename)}")

    except Exception as e:
        print(f"Error saving data: {e}")


def scroll_to_load_more(driver, max_scrolls=5):
    """Scroll gradually in four steps to load more partners if the page uses lazy loading."""
    for i in range(max_scrolls):
        print(f"Scrolling slowly (pass {i+1}/{max_scrolls})")
        height = driver.execute_script("return document.body.scrollHeight")
        
        # Scroll by quarters
        for fraction in [0.25, 0.5, 0.75, 1.0]:
            driver.execute_script(f"window.scrollTo(0, {height * fraction});")
            time.sleep(1.5)  # Let content load after each partial scroll


def main():
    """Main function to run the crawling script."""
    # We only need to focus on Cybersecurity tag directly in the extraction
    # But we can still filter for both tags to narrow down the results
    selected_hashtags = ["Cybersecurity"]  # Only filter for Cybersecurity initially
    selected_company_types = ["Startup"]  # Replace with desired company types or leave empty
    
    driver = setup_driver()
    
    try:
        # Access the partners page
        driver.get("https://vivatechnology.com/partners")
        print("Page loaded")
        
        # Wait for the page to load completely
        time.sleep(3)

        # Accept cookies
        accept_cookies(driver)

        time.sleep(1)
        
        # Select filters
        select_filters(driver, hashtags=selected_hashtags, company_types=selected_company_types)
        
        # Wait for results to load after applying filters
        time.sleep(5)
        
        scroll_to_load_more(driver)
        # Scroll to load more partners if needed
        #scroll_to_load_more(driver, max_scrolls=5)  # Increased to capture more partners

        time.sleep(2)
        
        # Extract partner data
        partners = extract_partner_data(driver)
        
        # Save data to CSV
        save_to_csv(partners)
        
        print(f"Completed! Found {len(partners)} cybersecurity partners with AI connection.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    main()