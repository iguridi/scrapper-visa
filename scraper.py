from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from browsermobproxy import Server
import time
import telegram_send
import random
import json

#edit these variables
browsermobproxy_PATH = 'browser_mob/bin/browsermob-proxy'
reschedule_url = "https://ais.usvisa-info.com/pt-br/niv/schedule/12312312/appointment?utf8=%E2%9C%93&applicants%5B%5D=12323123&applicants%5B%5D=3232323&applicants%5B%5D=32323&confirmed_limit_message=1&commit=Continuar"
email = 'user@gmail.com'
password = 'password'
consulates = {
    '54':'Brasília',
    '128': 'Porto Alegre',
    '57': 'Recife',    
    '55': 'RJ',
    '56': 'SP',
}

def init_proxy():
    path = browsermobproxy_PATH
    server = Server(path, options={'port': 8080})
    server.start()
    proxy = server.create_proxy()
    options = {'captureContent': True, 'captureHeaders': True}
    proxy.new_har('us_visa_log', options=options)
    return proxy

def random_number():
    return random.randint(10,40)/10

def init_page(proxy):
    url = reschedule_url
    option = webdriver.ChromeOptions()
    option.add_argument('--proxy-server={host}:{port}'.format(host="localhost", port=proxy.port))
    option.add_argument('--ignore-certificate-errors')
    option.add_argument('--disable-notifications')
    option.add_argument("--mute-audio")
    # comment the following line for if you want to test (otherwise it will open a headless Chrome instance)
    option.add_argument("--headless") 

    option.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)
    proxy.wait_for_traffic_to_stop(1, 60)
    driver.get(url)
    time.sleep(random_number())

    ok_button = driver.find_elements(By.XPATH,'/html/body/div[6]/div[3]/div/button')[0]
    ok_button.click()
    time.sleep(random_number())

    email_input = driver.find_element(By.XPATH, '//*[@id="user_email"]')
    email_input.send_keys(email)
    time.sleep(random_number())

    senha_input = driver.find_element(By.XPATH, '//*[@id="user_password"]')
    senha_input.send_keys(password)
    time.sleep(random_number())

    i_agree = driver.find_element(By.XPATH, '//*[@id="new_user"]/div[3]/label/div')
    i_agree.click()
    time.sleep(random_number())

    acessar = driver.find_element(By.XPATH, '//*[@id="new_user"]/p[1]/input')
    acessar.click()
    time.sleep(random_number())

    return driver

def find_json(har, cons):
    for ent in har:
        _url = ent['request']['url']
        if '{}.json?appointments[expedite]=false'.format(cons) in _url:
            _response = ent['response']
            if 'text' in _response['content']:
                data = _response['content']['text']
                if 'business_day' in data:
                    return json.loads(data)
    return False

def finished(dates):
    result = sum([dates[i]['success'] for i in dates])
    return result > len(consulates)

def clean_run(driver, proxy):    
    dates = {}
    for cons in consulates:
        dates[cons] = {
            'city': consulates[cons],
            'av_dates' : {},
            'success': 0
        }

    consulates = Select(driver.find_element(By.XPATH, '//*[@id="appointments_consulate_appointment_facility_id"]'))

    max_tries = 20
    current_try = 0
    while not finished(dates):
        current_try += 1
        if current_try > max_tries:
            break
        for cons in dates:
            #print('Trying to obtain available dates for {}'.format(cons))
            consulates.select_by_value(cons)
            response = find_json(proxy.har['log']['entries'], cons)
            if response:
                dates[cons]['av_dates'] = response
                dates[cons]['success'] = 1
                #print('success!')
            time.sleep(random_number())
    
    return dates

def find_best_date(av_dates):
    try:
        data = av_dates[0]['date']
    except:
        return "error"
    for d in av_dates:
        # edit the logic below if you want to filter for a specific time window. right now it only finds the earliest available date
        if d['date'] < data:
            data = d['date']
    return data

# running section
runs = 0
while True:
    try:
        runs += 1
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Run number {} ({}):".format(str(runs), current_time))
        proxy = init_proxy()
        driver = init_page(proxy)
        dates = clean_run(driver,proxy)
        result = []
        perfect_date = ""
        for cons in dates:
            data = find_best_date(dates[cons]['datas'])
            # this is the logic for when to shoot a Telegram message. edit it according to your needs
            if (
                data < '2022-01-10' 
                and dates[cons]['city'] == 'SP'
                and data > '2021-12-01'
            ):
                perfect_date = 'ATTENTION! OPENING FOUND FOR THE FOLLOWING CONSULATE -  {}: {}'.format(dates[cons]['city'],data)
            result.append('{}: {}'.format(dates[cons]['city'],data))
        if perfect_date != "":
            telegram_send.send(messages=[perfect_date])
        print("\n".join(result))
        print("*****************")
        time.sleep(random_number()*60)
        driver.quit()

    except KeyboardInterrupt:
        break

    # sorry for this :( but I didn't have time to test for all possible legit erorrs that might happen
    except:
        time.sleep(random_number()*30)
        continue
    