from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import json
import time
import re
import os

class LinkdenScraper:

    def __init__(self,driver,path_args = ()):
        self.driver =driver
        self.path_args = path_args
        try:
            with open(os.path.join(os.getcwd(),*path_args,'lk_jobs_data.json'),'r') as data:
                self.data = json.loads(data.read())
        except FileNotFoundError:
            with open(os.path.join(os.getcwd(),*path_args,'lk_jobs_data.json'),'w') as data:
                self.data = {}
                data.write(json.dumps(self.data))

    def num_applicants(self):
        """
        Grabs number of applicants from either the header of the
        applicants-insights div, or within the applicants-table in the same
        div element. Returns empty string if data is not available.
        """
        # use two selectors since LI has two methods of showing number
        # of applicants in the applicants-insights driver
        num_applicant_selectors = [
            "span.jobs-details-job-summary__text-ellipsis",
            "table.other-applicants-table.comparison-table tr td",
            "p.number-of-applicants"
        ]
        for selector in num_applicant_selectors:
            try:
                num_applicants = self.driver.find_element_by_css_selector(selector).text
            except Exception as e:
                pass
            else:
                return ''.join(list(filter(lambda c: c.isdigit(), num_applicants)))
        return ''

    def job_data(self, elem_link):
        """
        scrapes the posting info for title, company, post age, location,
        and page views. Have seen many strange errors surrounding the
        job title, company, location data, so have used many try-except
        statements to avoid potential errors with unicode, etc.
        """
        link = elem_link.get_attribute('href')
        job_name = elem_link.text
        elem_link.click()
        job_info = {
            "link": link,
            "job name": job_name,
            "company": self.driver.find_element_by_css_selector("a.jobs-details-top-card__company-url").text,
            "location": self.driver.find_element_by_class_name("jobs-details-top-card__bullet").text,
            "description": self.driver.find_element_by_id("job-details").text,
            'date_posted': 'n/a'
        }
        # click the 'read more' button to reveal more about the job posting
        return job_info

    def parse_post_age(self):
        age = self.driver.find_elements_by_css_selector("p.jobs-details-top-card__job-info")
        for a in age:
            ag = self.driver.find_elements_by_xpath("//p[@class='jobs-details-top-card__job-info']/child::*")
            aget = a.text
            post_age = re.findall(r'(?:\nPosted)\s([0-9]+ (hours?|days?|weeks?|months?))', aget)
        return post_age[0]

    def scrape_page(self, element):
        """
        scrapes single job page after the driver loads a new job posting.
        Returns data as a dictionary
        """
        # wait ~1 second for elements to be dynamically rendered
        time.sleep(1.2)
        start = time.time()

        applicant_info = {
            "num_applicants"    :  self.num_applicants(),
        #    "skills"            :  applicants_skills(driver),
        #    "education"         :  applicants_education(driver),
        #    "locations"         :  applicants_locations(driver)
        }

        data = {
        #    "applicant_info"    :  applicant_info,
            "job_info"          :  self.job_data(element),
            "job_age"         :  self.parse_post_age(),
        }
        print("scraped page in  {}  seconds\n".format(time.time()-start))

        post_title = data["job_info"]["job name"]+"_"+data["job_info"]["company"]
        self.data[post_title] = data

    def save_json(self):
        with open(os.path.join(os.getcwd(), *self.path_args, 'lk_jobs_data.json'), 'w') as data:
           data.write(json.dumps(self.data))