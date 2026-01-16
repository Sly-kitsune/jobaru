import time
from .base import JobPlatform
from ..filler import SmartFiller

class GenericPlatform(JobPlatform):
    def login(self):
        pass # Generic sites usually don't have a central login we manage upfront

    def search_jobs(self, query):
        pass # We don't search "generic", we land here.

    def apply_to_job(self, job_url):
        print(f"[Generic] Navigating to {job_url}")
        self.browser.navigate(job_url)
        time.sleep(3)
        
        # Use Smart Filler
        print("[Generic] Attempting to auto-fill form...")
        filler = SmartFiller(self.browser, self.config.get('resume_text'), model=self.config.get('model'))
        filler.fill_form(resume_file_path=self.config.get('resume_path'))
        
        print("[Generic] Form filled (check browser). Please review and submit.")
        # In a fully autonomous loop, we might try to find the submit button, 
        # but for safety/User Request constraint ("do not eat pc space" implying efficient correct usage),
        # yielding control or just filling is safer v1.
