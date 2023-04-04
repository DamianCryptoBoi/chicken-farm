import seleniumwire.undetected_chromedriver as uc
import time

d_list = []

# chrome_options.add_experimental_option("detach", True)

for i in range(0,3):
    driver = uc.Chrome()
    d_list.append(driver)

    # driver.get("https://whoer.net/")




time.sleep(100)