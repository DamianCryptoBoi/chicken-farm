import threading
import seleniumwire.undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support    import expected_conditions as EC
from seleniumbase import SB

import json

class ScrapeThread(threading.Thread):
	def __init__(self, url,email,password,confirm_email):
		threading.Thread.__init__(self)
		self.url = url
		self.email = email
		self.password = password
		self.confirm_email = confirm_email

	def run(self):
		with SB(uc=True, proxy="supabanana:supachupachup@108.165.195.142:23887") as driver:
			try:
				driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {'timezoneId': 'America/New_York'})
				driver.get('https://accounts.google.com/ServiceLogin')
				driver.sleep(3)
				driver.type('identifier', f'{self.email}\n', By.NAME)
				driver.sleep(3)
				driver.type( 'Passwd', f'{self.password}\n', By.NAME)
				driver.sleep(3)
				try:
					driver.driver.find_elements(By.CLASS_NAME, "vxx8jf")[2].click()
					driver.sleep(2)
					driver.type('knowledgePreregisteredEmailResponse', f'{self.confirm_email}\n', By.NAME)
					driver.sleep(2)
				except:
					pass

				try:
					driver.get("https://www.youtube.com/")
					driver.sleep(20)
				except:
					pass
				ck = driver.driver.get_cookies()
				json_object = json.dumps(ck, indent=4)
				with open(f"./cookies/{self.email}.json", "w") as outfile: 
					outfile.write(json_object)
			except:
				print(f"Error: {self.email} can not get cookies")
			print(f'Get cookies success: {self.email}')
			driver.driver.close()
			


urls = [
	'',
]

threads = []
for url in urls:
	t = ScrapeThread(url,"nguyenthanhbop20@gmail.com","nguyenthanhbop","nguyenthanhbopmxwn@gmail.com")
	t.start()
	threads.append(t)

for t in threads:
	t.join()
