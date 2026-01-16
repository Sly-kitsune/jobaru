import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SmartFiller:
    def __init__(self, browser, config):
        """
        :param browser: The BrowserEngine instance
        :param config: The user configuration dict (contains resume_path, etc.)
        """
        self.browser = browser
        self.config = config
        self.driver = browser.driver

    def fill_easy_apply_page(self, cover_letter=None):
        """
        Scans the current modal page and attempts to fill known fields.
        Returns:
            bool: True if it did something or looks safe, False if user intervention needed.
        """
        print("   [SmartFiller] Scanning page...")
        
        # 1. Handle File Upload (Resume)
        # Look or input[type='file']. If present and accepts PDF/Doc, upload resume.
        file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        for inp in file_inputs:
            # Check if it's already filled? Hard to tell for file inputs usually.
            # But usually LinkedIn asks to upload if not present.
            try:
                # We assume if there's a file input, it's for the resume/cover letter doc
                # Check label if possible
                resume_path = self.config.get('resume_path')
                if resume_path:
                    # Send keys requires the element to be present, but sometimes hidden.
                    # Selenium handles hidden file inputs usually if we send to the input element itself.
                    inp.send_keys(resume_path)
                    print(f"   [SmartFiller] Uploaded resume: {resume_path}")
                    time.sleep(1)
            except Exception as e:
                print(f"   [SmartFiller] upload warning: {e}")

        # 2. Handle Text Inputs (Mobile, City, etc.) - simple heuristics
        text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='tel']")
        for inp in text_inputs:
            if inp.get_attribute("value"):
                continue # Already filled (LinkedIn pre-fill)
            
            # Label check?
            # This is hard to do robustly without complex DOM traversal.
            # For now, we trust LinkedIn pre-fill. If empty + required, we'll flag it.
            pass

        # 3. Handle Cover Letter (Textarea)
        if cover_letter:
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            for ta in textareas:
                # likely the cover letter field if visible
                if ta.is_displayed():
                    current_val = ta.get_attribute("value")
                    if len(current_val) < 10: # Empty or just default text
                        ta.clear()
                        ta.send_keys(cover_letter)
                        print("   [SmartFiller] Pasted cover letter.")
                        time.sleep(1)

        return True

    def has_unanswered_questions(self):
        """
        Checks for visible input fields that might need user attention.
        Returns true if it finds visible radio sets, dropdowns, or empty required text fields.
        """
        # 1. Radio Buttons (Fieldsets usually)
        # LinkedIn uses fieldsets for radio groups. If any fieldset is visible, we might need to pick one.
        # We can perform a rudimentary check: is any radio within it checked?
        fieldsets = self.driver.find_elements(By.CSS_SELECTOR, "fieldset")
        for fs in fieldsets:
            if fs.is_displayed():
                # Check if any radio child is checked
                radios = fs.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                if radios:
                    is_checked = any(r.is_selected() for r in radios)
                    if not is_checked:
                        print("   [SmartFiller] Found unanswered radio question.")
                        return True

        # 2. Dropdowns (Select)
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        for sel in selects:
             if sel.is_displayed():
                 # Default value is often empty or "Select..."
                 if not sel.get_attribute("value"):
                     print("   [SmartFiller] Found unanswered dropdown.")
                     return True

        # 3. Text Inputs (Required ones)
        # This is strictly heuristics. We look for inputs that are visible and empty.
        text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='tel']")
        for inp in text_inputs:
            if inp.is_displayed() and not inp.get_attribute("value"):
                 print("   [SmartFiller] Found empty text input.")
                 return True

        # 4. Textareas (Open-ended questions)
        textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
        for ta in textareas:
            if ta.is_displayed() and not ta.get_attribute("value"):
                 print("   [SmartFiller] Found empty textarea.")
                 return True
                 
        return False

    def check_errors(self):
        """Checks for visible error messages on the form."""
        errors = self.driver.find_elements(By.CSS_SELECTOR, ".artdeco-inline-feedback__message")
        visible_errors = [e for e in errors if e.is_displayed()]
        if visible_errors:
            print(f"   [SmartFiller] Detected {len(visible_errors)} validation errors.")
            return True # Has errors
        return False
