import time
import os
from .base import JobPlatform
from .generic import GenericPlatform
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LinkedIn(JobPlatform):
    def login(self):
        """
        Logs in to LinkedIn. 
        Note: This is sensitive to bot detection. 
        For this persistent local agent, we assume user logs in once manually 
        or we use a specified cookie if 'pc space' allows.
        For now, we pause and ask user to login if not detected.
        """
        print("[LinkedIn] checking login...")
        self.browser.navigate("https://www.linkedin.com/feed/")
        if "login" in self.browser.current_url():
            print("Please log in to LinkedIn in the browser window manually.")
            input("Press Enter after you have logged in...")
        
    def __init__(self, browser, config):
        super().__init__(browser, config)
        self.history_path = os.path.join("applications", "history.json")
        self.processed_jobs = self._load_history()

    def _load_history(self):
        import json
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r') as f:
                    return set(json.load(f))
            except: return set()
        return set()

    def _save_history(self, job_id):
        import json
        self.processed_jobs.add(job_id)
        try:
            os.makedirs("applications", exist_ok=True)
            with open(self.history_path, 'w') as f:
                json.dump(list(self.processed_jobs), f)
        except Exception as e:
            print(f"[Warn] Failed to save history: {e}")

    def _get_job_id(self, url):
        # Extract numeric ID from linkedin url
        import re
        match = re.search(r"view/(\d+)", url) or re.search(r"currentJobId=(\d+)", url)
        return match.group(1) if match else url

    def search_jobs(self, query, location="Remote"):
        # Sort by Date (DD) and filter to Past 24 Hours (r86400) to ensure freshness
        url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}&sortBy=DD&f_TPR=r86400"
        self.browser.navigate(url)
        time.sleep(3)
        
        job_results = []
        # Scroll results to load more
        # Scroll results to load more
        print("[LinkedIn] Scrolling deeper for more results...")
        try:
            results_container = self.browser.driver.find_element(By.CSS_SELECTOR, ".jobs-search-results-list")
            # Scroll significantly more to load backlog
            for _ in range(15):
                self.browser.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 1000;", results_container)
                time.sleep(1)
        except:
             # Fallback for main window scroll
             for _ in range(10):
                self.browser.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

        # Collect cards
        card_selector = ".job-card-container, li.jobs-search-results__list-item"
        cards = self.browser.driver.find_elements(By.CSS_SELECTOR, card_selector)
            
        print(f"[LinkedIn] Found {len(cards)} total cards. Filtering for fresh ones...")

        processed_count = 0
        for i, card in enumerate(cards):
            # Limit to processing 50 fresh jobs per run
            if len(job_results) >= 50: break
            
            try:
                # Attempt to find anchor (title link)
                anchor = None
                selectors = ["a.job-card-list__title", "a.base-card__full-link", "a.job-card-container__link", ".job-card-list__title"]
                
                for sel in selectors:
                    try:
                        el = card.find_element(By.CSS_SELECTOR, sel)
                        if el.get_attribute("href"):
                            anchor = el
                            break
                    except: continue
                
                if anchor:
                    url = anchor.get_attribute("href")
                    job_id = self._get_job_id(url)
                    
                    # HISTORY CHECK
                    if job_id in self.processed_jobs:
                         # print(f"   [Skip] Already applied: {job_id}")
                         continue
                    
                    title = anchor.text.strip() or anchor.get_attribute("aria-label") or "Unknown Role"
                    
                    # Try company
                    company = "Unknown"
                    try:
                        company = card.find_element(By.CSS_SELECTOR, ".job-card-container__company-name").text.strip()
                    except: pass
                        
                    job_results.append({
                        "title": title,
                        "company": company,
                        "url": url,
                        "id": job_id
                    })
            except Exception as e:
                pass
        
        print(f"[LinkedIn] Identified {len(job_results)} NEW jobs to apply to.")
        return job_results
        
        print(f"[LinkedIn] Returning {len(job_results)} parsed jobs.")
        return job_results

    def apply_to_job(self, job_url, cover_letter=None):
        print(f"[LinkedIn] Viewing job: {job_url}")
        self.browser.navigate(job_url)
        time.sleep(2)
        
        # Check for Easy Apply or External
        # BROAD SEARCH FOR APPLY BUTTON
        print("[LinkedIn] Hunting for Apply button...")
        easy_apply_btn = None
        
        # Strategy 1: Explicit "Easy Apply" Text (Best for intended target)
        try:
            # Look for button or link with "Easy Apply" text or aria-label
            xpath_easy = "//*[(self::button or self::a) and (contains(., 'Easy Apply') or contains(@aria-label, 'Easy Apply'))]"
            candidates = self.browser.driver.find_elements(By.XPATH, xpath_easy)
            for c in candidates:
                if c.is_displayed():
                    easy_apply_btn = c
                    print("[LinkedIn] Found explicit 'Easy Apply' button.")
                    break
        except: pass

        # Strategy 2: Data Attribute (Stable but might be generic)
        if not easy_apply_btn:
            try:
                candidates = self.browser.driver.find_elements(By.CSS_SELECTOR, "[data-view-name='job-apply-button']")
                for c in candidates:
                    if c.is_displayed():
                        # specific check to prefer Easy Apply if multiple
                        if "Easy Apply" in c.text or "Easy Apply" in c.get_attribute("aria-label") or not easy_apply_btn:
                             easy_apply_btn = c
            except: pass
            if easy_apply_btn: print("[LinkedIn] Found button via data-view-name.")

        # Strategy 3: Generic "Apply" Text (Fallback)
        if not easy_apply_btn:
            try:
                xpath = "//*[(self::button or self::a) and contains(., 'Apply') and not(contains(., 'Applied'))]"
                candidates = self.browser.driver.find_elements(By.XPATH, xpath)
                for c in candidates:
                    if c.is_displayed():
                        easy_apply_btn = c
                        print(f"[LinkedIn] Found button via fallback text: '{c.text}'")
                        break
            except Exception as e:
                print(f"[LinkedIn] Xpath error: {e}")

        if not easy_apply_btn:
             print("[LinkedIn] Primary 'Apply' button NOT found.")
             # CAPTURE DEBUG ARTIFACTS
             try:
                 debug_dir = os.path.join("applications", "debug_html")
                 os.makedirs(debug_dir, exist_ok=True)
                 timestamp = time.strftime("%H%M%S")
                 
                 # Screenshot
                 shot_path = os.path.join(debug_dir, f"apply_fail_{timestamp}.png")
                 self.browser.driver.save_screenshot(shot_path)
                 
                 # HTML
                 html_path = os.path.join(debug_dir, f"apply_fail_{timestamp}.html")
                 with open(html_path, "w", encoding="utf-8") as f:
                     f.write(self.browser.driver.page_source)
                     
                 print(f"[LinkedIn] Saved debug screenshot to: {shot_path}")
             except Exception as e:
                 print(f"[LinkedIn] Failed to save debug info: {e}")

             return

        print("[LinkedIn] 'Apply' button found. Clicking...")
        
        # Click Apply with Retry Logic
        modal_present = False
        try:
            # Scroll into view first
            self.browser.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", easy_apply_btn)
            time.sleep(1)
            
            easy_apply_btn.click()
            # Wait for modal - Broadened selector and increased timeout
            WebDriverWait(self.browser.driver, 10).until(
                lambda d: d.find_element(By.CSS_SELECTOR, ".jobs-easy-apply-content") or 
                          d.find_element(By.CSS_SELECTOR, "[role='dialog']")
            )
            modal_present = True
        except:
             print("[LinkedIn] Standard click failed or modal didn't appear. Retrying with JS...")
             try:
                 self.browser.driver.execute_script("arguments[0].click();", easy_apply_btn)
                 WebDriverWait(self.browser.driver, 10).until(
                    lambda d: d.find_element(By.CSS_SELECTOR, ".jobs-easy-apply-content") or 
                              d.find_element(By.CSS_SELECTOR, "[role='dialog']")
                 )
                 modal_present = True
             except:
                 pass

        time.sleep(3)
        
        # Check if external (New window) - If so, we are done
        if len(self.browser.driver.window_handles) > 1:
            print("[LinkedIn] Redirected to external site. Autonomous apply stopped.")
            self.browser.driver.switch_to.window(self.browser.driver.window_handles[-1])
            self.browser.driver.close()
            self.browser.driver.switch_to.window(self.browser.driver.window_handles[0])
            return

        if not modal_present:
             print("[LinkedIn] Error: Easy Apply modal did not appear. (Might be external or blocked).")
             # Capture debug
             try:
                 timestamp = time.strftime("%H%M%S")
                 debug_dir = os.path.join("applications", "debug_html")
                 os.makedirs(debug_dir, exist_ok=True)
                 
                 # Screenshot
                 self.browser.driver.save_screenshot(os.path.join(debug_dir, f"modal_fail_{timestamp}.png"))
                 
                 # HTML Source
                 with open(os.path.join(debug_dir, f"modal_fail_{timestamp}.html"), "w", encoding="utf-8") as f:
                     f.write(self.browser.driver.page_source)
                     
                 print(f"[LinkedIn] Debug artifacts saved to {debug_dir}")
             except Exception as e: 
                 print(f"[LinkedIn] Failed to save debug info: {e}")
             return

        # Internal Easy Apply Flow
        print("[LinkedIn] Starting Easy Apply flow...")
        from ..filler import SmartFiller
        filler = SmartFiller(self.browser, self.config)
        
        # Loop through steps
        max_steps = 15
        step = 0
        while step < max_steps:
            step += 1
            time.sleep(2)
            
            # 1. Check for Primary Action Button (Next/Review/Submit)
            # Strategy: Find any visible button that looks like a primary action inside the modal
            primary_btn = None
            
            # Text targets
            targets = ["submit application", "review", "next"]
            
            try:
                # Try locating by text content (robust for localized/class-changing UIs)
                for t in targets:
                    xpath = f"//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{t}')]"
                    btns = self.browser.driver.find_elements(By.XPATH, xpath)
                    for btn in btns:
                        if btn.is_displayed() and "artdeco-button--primary" in btn.get_attribute("class"):
                             primary_btn = btn
                             break
                    if primary_btn: break
                
                # Fallback to just class if text match failed
                if not primary_btn:
                     btns = self.browser.driver.find_elements(By.CSS_SELECTOR, "button.artdeco-button--primary")
                     for btn in btns:
                         if btn.is_displayed():
                             primary_btn = btn
                             break
            except Exception as e:
                print(f"   [Debug] Error finding button: {e}")

            if not primary_btn:
                print("   [Auto-Apply] No primary button found. Waiting 2s more...")
                time.sleep(2)
                # Retry once
                btns = self.browser.driver.find_elements(By.CSS_SELECTOR, "button.artdeco-button--primary")
                for btn in btns:
                     if btn.is_displayed():
                         primary_btn = btn
                         break
                
            if not primary_btn:
                # One last check: Did we already succeed? (Greentick / 'Application sent')
                if "application sent" in self.browser.driver.page_source.lower():
                     print("   [Auto-Apply] Application Sent detected!")
                     # Try finding 'Done' button
                     try:
                         done_btn = self.browser.driver.find_element(By.XPATH, "//button[contains(., 'Done')]")
                         done_btn.click()
                     except: pass
                     return

                print("   [Auto-Apply] Still no primary button. Stuck? Manual intervention needed.")
                input("   >>> check browser. Press Enter to continue loop...")
                continue # Retry loop

            btn_text = primary_btn.text.lower()
            print(f"   [Auto-Apply] Step {step}: Found button '{btn_text}'")

            # 2. Fill Page
            filler.fill_easy_apply_page(cover_letter)
            
            # 3. Check for Errors OR Unanswered Questions OR Critical Step
            has_errors = filler.check_errors()
            needs_input = filler.has_unanswered_questions()
            
            # Auto-Pause on Submit/Review to let user verify
            is_critical_step = 'submit' in btn_text or 'review' in btn_text
            
            if has_errors or needs_input or is_critical_step:
                if has_errors: reason = "Validation Errors"
                elif needs_input: reason = "Unanswered Questions"
                else: reason = f"Critical Step ({btn_text})"
                
                print(f"   [Auto-Apply] {reason} detected. Pausing for manual input.")
                print("   ****************************************************")
                print("   ***  PAUSED: Verify form/answers in browser      ***")
                print("   ***  Press Enter in terminal to PROCEED/SUBMIT   ***")
                print("   ****************************************************")
                input("   >>> Waiting for user confirmation...")

            # 4. Click Next/Review/Submit
            try:
                if 'submit' in btn_text:
                    print("   [Auto-Apply] Submitting application...")
                    primary_btn.click()
                    time.sleep(3)
                    print("   [Auto-Apply] Application Submitted!")
                    
                    # Verify Success
                    if "application sent" in self.browser.driver.page_source.lower():
                        print("   [Auto-Apply] Success confirmed.")
                    
                    try:
                        dismiss_btn = self.browser.driver.find_element(By.CSS_SELECTOR, "[aria-label='Dismiss']")
                        if dismiss_btn: dismiss_btn.click()
                    except:
                        pass
                    return
                else:
                    primary_btn.click()
            except Exception as e:
                print(f"   [Auto-Apply] Error clicking button: {e}")
                input("   >>> Fix manually and press Enter...")

        print("[Auto-Apply] Max steps reached.")
        # Mark as processed (even if max steps reached, we tried)
        # Assuming we can get 'id' context if we pass it, but for now we extract from current URL
        job_id = self._get_job_id(self.browser.current_url())
        self._save_history(job_id)
