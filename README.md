# scraper_us_visa

DISCLAIMER: USE THIS AT YOUR OWN RISK. 

This script logs into your US visa scheduling account and loops through all consulates that you wish in your country, gathering all available dates and sending you a notification in your phone if it finds a date that fits what you were looking for. You'll still need to manually log in and reschedule your appointment. You can change the periodicity as you wish - the default logic is one request every ~5 mins.

This was built in one sleepless night and not thoroughly tested - it's simply a quick hack! But it worked for me. Feel free to adapt to your needs as you wish.

In order to run the script, you'll need to install the following python packages: 
- selenium and its Chrome web driver (it will simulate a real user's navigation)
- browsermobproxy (to read the json files from the server responses)
- telegram_send (to send a Telegram message to your bot)

Yes, you'll need a Telegram account and a bot, which is super easy to create. Just follow the instructions on https://pypi.org/project/telegram-send/. You'll need to enter your bot's credentials into your command line, from the same virtual environment you're running the python script from.

The initial variables should be self-explanatory, except for **reschedule_url** and the **consulates** dict. Here are the steps you should do in order to fetch them:

1. Log into your account on https://ais.usvisa-info.com
2. Click continue on the party you want to reschedule
3. Click on "Reschedule Interview"
<img width="637" alt="Captura de Tela 2021-10-28 às 2 44 43 PM" src="https://user-images.githubusercontent.com/4325876/139318253-31dead80-676f-439c-bfd1-3c2100f16db3.png">
4. Hit continue again
5. You'll find yourself in the main rescheduling page. This is the url you should use instead of the mock one provided on **reschedule_url**.
6. As for the **consulates** dictionary, right click on the first select and click on "Inspect Element" 
<img width="341" alt="Captura de Tela 2021-10-28 às 2 46 28 PM" src="https://user-images.githubusercontent.com/4325876/139318555-e6f22771-1f77-49f5-be50-f95195e15767.png">
7. Each <option> element is a city. Then, copy and paste the city names and their values into the **consulates** dict. You don't need to pick all cities - just add the ones that make sense to you, even if only one.
<img width="435" alt="Captura de Tela 2021-10-28 às 2 46 54 PM" src="https://user-images.githubusercontent.com/4325876/139318642-67eb20bc-8ed8-456c-9d77-3603527599e9.png">

Also, don't forget to edit the date comparison logic to find the best date for your needs, nor the message sending logic (i.e. in what conditions the bot will ping your phone). Personally, I leave my phone notifications always muted, but Telegram lets you create exceptions for which it will trigger a real notification (with sound, buzz, etc). This way the bot could even wake me up at night if necessary (yes, I was this desperate).
  
Good luck!
