# DuinoWallet
This bot allows Duino Coin users to manage their DUCOs and perform various wallet-related tasks through Telegram.

### Features
* Automatically recharge your balance
* Automatically withdraw funds
* Send funds between users

### Prerequisites
* Python 3.6 or later.
* Python modules in ```requirements.txt``` 

```bash
pip install -r requirements.txt
```
### Configuration
To host this bot you'll need to create if not exist the ```users``` folder that will contains users info.
You'll also have to edit lines 7-11 with your data.

```python
TELEGRAM_TOKEN = ""   # Change with your bot token (from @BotFather)
ADMIN_ID = 000000    # Change with your Telegram ID
DUINO_USERNAME = ''   # Change with your Duino-Coin username
DUINO_PASSWORD = '' # Change with your Duino-Coin password
```
## Usage
To start the script, simply run the following command:

```bash
python bot.py
```
