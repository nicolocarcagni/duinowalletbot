import telepot   # pip install telepot
import requests # pip install requests
import os
import random
import json

TELEGRAM_TOKEN = ""   # Change with your bot token (from @BotFather)
USERS_DIR = 'users/'    # Directory where user data is stored
ADMIN_ID = 000000    # Change with your Telegram ID
DUINO_USERNAME = 'Nikolovich'   # Change with your Duino-Coin username
DUINO_PASSWORD = '' # Change with your Duino-Coin password

def load_user_data(user_id):   # Load user data from file
    filename = f"{USERS_DIR}{user_id}.txt"
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    else:   # Create a file for the user if it doesn't exist
        user_data = {'balance': 0, 'dusername': None, 'used_transaction_codes': []}
        save_user_data(user_id, user_data)
        return user_data


def save_user_data(user_id, data):  # Save user data to file
    filename = f"{USERS_DIR}{user_id}.txt"
    with open(filename, 'w') as file:
        json.dump(data, file)


def generate_random_string():   # Generate a random string of 10 characters for transaction code
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))


def verify_transaction(user_id, transaction_code): # Verify a transaction and return the amount if valid
    user_data = load_user_data(user_id)
    
    if transaction_code in user_data['used_transaction_codes']: # Check if transaction code has already been used
        return None
    
    url = f"https://server.duinocoin.com/user_transactions/{DUINO_USERNAME}"  # Get transactions from Duino-Coin API, change username to yours
    response = requests.get(url)
    data = response.json()

    for transaction in data['result']:  # Check if transaction code is valid
        if (
            transaction['memo'] == transaction_code
            and transaction['recipient'] == DUINO_USERNAME # Change username to yours
        ):
            user_data['used_transaction_codes'].append(transaction_code)
            save_user_data(user_id, user_data)
            return transaction['amount']
    return None


def IDfromDusername(dusername): # Find user ID by dusername
    for filename in os.listdir(USERS_DIR):
        if filename.endswith(".txt"):
            with open(os.path.join(USERS_DIR, filename), 'r') as file:
                user_data = json.load(file)
                if user_data['dusername'] == dusername:
                    return filename.split('.')[0]  # Restituisci l'ID utente senza l'estensione .txt
    return None


def send(user_id, recipient_dusername, amount): # Send funds to another user
    sender_data = load_user_data(user_id)
    recipient_id = IDfromDusername(recipient_dusername)

    if recipient_id is None:
        return "⚠️*User not found.*"

    recipient_data = load_user_data(recipient_id)

    if amount <= 0:
        return "⚠️*Invalid amount.*"
    
    if amount > sender_data['balance']:
        return "⚠️*You don't have enough funds to send that amount.*"

    sender_data['balance'] -= amount
    recipient_data['balance'] += amount

    save_user_data(user_id, sender_data)
    save_user_data(recipient_id, recipient_data)

    send_notification(recipient_id, f"💸*You received {amount} ᕲ from {sender_data['dusername']}.*")

    return f"💸*Succesfully sent {amount} ᕲ to {recipient_dusername}.*"


def send_notification(recipient_id, message):   # Notify the user of an incoming transaction
    bot.sendMessage(recipient_id, message, parse_mode='Markdown')


def withdraw(user_id, amount): # Withdraw funds from user's balance
    user_data = load_user_data(user_id)
    if user_data['dusername'] is None:
        return "⚠️*You must first initialize your profile with* `/init yourduinoname`"
    
    if not isinstance(amount, (float, int)) or amount <= 0:
        return "⚠️*Invalid amount.*"

    if amount < 10: # Minimum withdrawal you can change it
        return "⚠️*Minimum withdrawal amount is 10 ᕲ.*"

    if amount > user_data['balance']:
        return "⚠️*You don't have enough funds to withdraw that amount.*"

    params = { # Withdraw funds using Duino-Coin API
        'username': DUINO_USERNAME,
        'password': DUINO_PASSWORD, # Change password to yours
        'recipient': user_data['dusername'],
        'amount': amount,
        'memo': 'Withdraw from Duino Wallet Bot' # Change memo to whatever you want
    }

    response = requests.get("https://server.duinocoin.com/transaction", params=params)
    result = response.json() 

    if result['success']:
        user_data['balance'] -= amount
        save_user_data(user_id, user_data)
        return f"💸*Succesfully withdrew {amount} ᕲ. Your current balance is {user_data['balance']} ᕲ.*"
    else:
        return f"⚠️*An error occurred while processing your withdrawal. Please try again later.*"

def list_users(user_id):
    user_list = []
    for filename in os.listdir(USERS_DIR):
        if filename.endswith(".txt"):
            with open(os.path.join(USERS_DIR, filename), 'r') as file:
                user_data = json.load(file)
                user_list.append(f"➖{user_data['dusername']} - 💰 {user_data['balance']} ᕲ")
    if user_list:
        return "\n".join(user_list)
    else:
        return "⚠️*No users found.*"


def handle_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == 'text':
        user_id = msg['from']['id']
        command = msg['text'].split()

        if command[0] == '/start': # User initiated the bot
            # User initiated the bot
            user_data = load_user_data(user_id)
            if user_data['dusername'] is None:
                bot.sendMessage(chat_id, f"📍*Welcome! Before getting started, initialize the bot with* `/init yourduinoname`", parse_mode='Markdown')
            else:
                bot.sendMessage(chat_id, f"📍*Welcome back {user_data['dusername']}! Your current balance is* {user_data['balance']} ᕲ.", parse_mode='Markdown')
                bot.sendMessage(chat_id, "❓*Type /help to get a list of available commands.*", parse_mode='Markdown')

        elif command[0] == '/init': # User wants to initialize their profile
            if len(command) == 2:
                dusername = command[1]
                user_data = load_user_data(user_id)
                if user_data['dusername'] is None:
                    user_data['dusername'] = dusername
                    save_user_data(user_id, user_data)
                    bot.sendMessage(chat_id, "☑️*Initialization successful!*", parse_mode='Markdown') 
                    bot.sendMessage(chat_id, "*You can now deposit on your balance with /deposit*", parse_mode='Markdown')
                else:
                    bot.sendMessage(chat_id, "⚠️*You already did it. If you want to change your username type* `/username yourduinoname`", parse_mode='Markdown')
            else:
                bot.sendMessage(chat_id, "⚠️*Syntax error. Use /init* _yourduinoname_", parse_mode='Markdown')

        elif command[0] == '/deposit': # User wants to deposit their balance
            user_data = load_user_data(user_id)
            if user_data['dusername'] is None:
                bot.sendMessage(chat_id, "⚠️*You must first initialize your profile with* `/init yourduinoname`", parse_mode='Markdown')
            else:
                transaction_code = generate_random_string()
                bot.sendMessage(chat_id, f"💰*To deposit your balance, send any amount to `Nikolovich` and use the following code as memo:* `{transaction_code}`", parse_mode='Markdown')
                bot.sendMessage(chat_id, f"⚠️*Then type /check* _transaction-code_ *to update your balance.*", parse_mode='Markdown')

        elif command[0] == '/check': # User wants to verify a transaction
            user_data = load_user_data(user_id)
            if user_data['dusername'] is None:
                bot.sendMessage(chat_id, "⚠️*You must first initialize your profile with* `/init yourduinoname`", parse_mode='Markdown')
            elif len(command) == 2:
                transaction_code = command[1]
                amount = verify_transaction(user_id, transaction_code)
                if amount is not None: 
                    user_data = load_user_data(user_id)
                    user_data['balance'] += amount
                    save_user_data(user_id, user_data)
                    bot.sendMessage(chat_id, f"☑️*Transaction verified successfully! Your balance has been deposited by* {amount} ᕲ. *💰Current balance:* {user_data['balance']} ᕲ.", parse_mode='Markdown')
                else:
                    bot.sendMessage(chat_id, "⚠️*Invalid or already used transaction. Please try again.*", parse_mode='Markdown')
            else:
                bot.sendMessage(chat_id, "⚠️*Syntax error. Use /check* _transactioncode_", parse_mode='Markdown')

        elif command[0] == '/balance': # User wants to check their balance
            user_data = load_user_data(user_id)
            if user_data['dusername'] is None:
                bot.sendMessage(chat_id, f"⚠️*You must first initialize your profile with* `/init yourduinoname`", parse_mode='Markdown')
            else:
                bot.sendMessage(chat_id, f"💰*Your current balance is* {user_data['balance']} ᕲ.", parse_mode='Markdown')

        elif command[0] == '/username': # User wants to change their dusername
            user_data = load_user_data(user_id)
            if user_data['dusername'] is None:
                bot.sendMessage(chat_id, "⚠️*You must first initialize your profile with* `/init yourduinoname`", parse_mode='Markdown')
            if len(command) == 2:
                dusername = command[1]
                user_data = load_user_data(user_id)
                user_data['dusername'] = dusername
                save_user_data(user_id, user_data)
                bot.sendMessage(chat_id, "☑️*Username changed successfully!*", parse_mode='Markdown')
            else:
                bot.sendMessage(chat_id, "⚠️*Syntax error. Use /username* _yourduinoname_", parse_mode='Markdown')

        elif command[0] == '/send': # User wants to send funds to another user
                    if len(command) == 3:
                        recipient_dusername = command[1]
                        try:
                            amount = float(command[2])
                            send_result = send(user_id, recipient_dusername, amount)
                            bot.sendMessage(chat_id, send_result, parse_mode='Markdown')
                        except ValueError:
                            bot.sendMessage(chat_id, "⚠️*Value error. Check your input.*", parse_mode='Markdown')
                    else:
                        bot.sendMessage(chat_id, "⚠️*Syntax error. Use /send* _username_ _amount_", parse_mode='Markdown')

        elif command[0] == '/withdraw': # User wants to withdraw their balance
            user_data = load_user_data(user_id)
            if user_data['dusername'] is None:
                bot.sendMessage(chat_id, "⚠️*You must first initialize your profile with* `/init yourduinoname`", parse_mode='Markdown')
            if len(command) == 2:
                try:
                    amount = float(command[1])
                    withdrawal_result = withdraw(user_id, amount)
                    bot.sendMessage(chat_id, withdrawal_result, parse_mode='Markdown')
                except ValueError:
                    bot.sendMessage(chat_id, "⚠️*Value error. Check your input.*", parse_mode='Markdown')
            else:
                bot.sendMessage(chat_id, "⚠️*Syntax error. Use /withdraw* _amount_", parse_mode='Markdown')
        
        elif command[0] == '/ls':
                if user_id == ADMIN_ID:
                    user_list_result = list_users(user_id)
                    bot.sendMessage(chat_id, user_list_result, parse_mode='Markdown')
                else:
                    bot.sendMessage(chat_id, "⚠️*You don't have permission to use this command.*", parse_mode='Markdown')

        elif command[0] == '/help': # User wants to see the help message
            bot.sendMessage(chat_id, "📍*Available commands:*\n\n"
                "/deposit - *Deposit on your balance.*\n"
                "/check _transaction-code_ - *Verify a transaction code and update your balance.*\n"
                "/balance - *Check your current balance.*\n"
                "/username _yourduinoname_ - *Change your Duino-Coin username.*\n"
                "/send _DuinoUsername_ _amount_ - *Send funds to another user.*\n"
                "/withdraw _amount_ - *Withdraw your balance to your Duino-Coin wallet.*\n"
                "/help - *Show this message.*", parse_mode='Markdown')  

        else: # Invalid command
            bot.sendMessage(chat_id, "⚠️*Invalid command. Type /help to get a list of available commands.*", parse_mode='Markdown')

# Start the bot
bot = telepot.Bot(TELEGRAM_TOKEN)
bot.message_loop(handle_message)

print('Bot is running...')
while True:
    pass
