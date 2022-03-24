#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author github.com/LimerBoy

__all__ = []

# Import modules
import os
import asyncio
import timeago
import pickledb
import threading
from flask import *
from aiogram import *
# Import packages
from core.db import *
from core.util import *
from core.account import *

# Read config
config = pickledb.load('config.json', False)

# Initialize HTTP server
http = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))
http.secret_key = config.get('secret_key')

# Initialize bot and dispatcher
bot = Bot(token=config.get('token'))
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def register(message: types.Message):
    # Get chat id
    client = Client.select().where(
        Client.chat_id == message.chat.id
    )
    # Register client if not exists
    if not client.exists():
        Client.create(
            chat_id=message.chat.id,
            full_name=message.chat.full_name
        )

    await message.reply("🌺 Usage:"
                        "\n/report"
                        "\nEnter description"
                        "\nThen upload photo")


@dp.message_handler(commands=['report'])
async def report(message: types.Message):
    await message.reply("❓ Please enter description ...")
    # Set WAITING_DESCRIPTION state
    Client.update(
        incident_state=IncidentStates.WAITING_DESCRIPTION.value
    ).where(
        Client.chat_id == message.chat.id
    ).execute()


@dp.message_handler()
async def description(message: types.Message):
    # Get chat id
    client = Client.select().where(
        Client.chat_id == message.chat.id
    )
    # Check if current state is WAITING_DESCRIPTION
    if IncidentStates(client.get().incident_state) == IncidentStates.WAITING_DESCRIPTION:
        incident_id = Incident.create(
            created_by=client,
            description=message.text
        )
        # Set WAITING_IMAGE state
        Client.update(
            incident_state=IncidentStates.WAITING_IMAGE.value,
            latest_incident_id=incident_id
        ).where(
            Client.chat_id == message.chat.id
        ).execute()
        # Information
        await message.reply("❓ Please attach image ...")


@dp.message_handler(content_types=['photo'])
async def photo(message):
    # Get chat id
    client = Client.select().where(
        Client.chat_id == message.chat.id
    ).get()
    # Check if current state is WAITING_DESCRIPTION
    if IncidentStates(client.incident_state) == IncidentStates.WAITING_IMAGE:
        data = await message.photo[-1].download()
        # Set COMPLETED state
        Client.update(
            incident_state=IncidentStates.COMPLETED.value
        ).where(
            Client.chat_id == message.chat.id
        ).execute()
        # Insert image
        Incident.update(
            image_path=data.name,
            created_by_id=client.id
        ).where(
            Incident.id == client.latest_incident_id
        ).execute()
        # Information
        await message.reply("❓ Incident reported")


@http.route('/dashboard', methods=['GET'])
@login_required
def dashboard(account: Administrator) -> str:
    def getAuthorName(id: int) -> str:
        for c in Client.select().where(Client.id == id):
            return c.full_name

    return render_template('dashboard.html',
                           reports=Incident.select(),
                           getAuthorName=getAuthorName,
                           getTimeAgo=timeago.format
                           )


@http.route('/settings', methods=['GET', 'POST'])
@login_required
def settings(account: Administrator):
    if request.method == 'POST':
        # Fetch credentials
        account_password = escape(request.form.get('accountPassword'))
        # Update credentials
        if account_password:
            account.set_password(account_password)
            return redirect(url_for('login'), code=302)

    return render_template('settings.html')


@http.route('/view/<int:img_id>', methods=['GET'])
@login_required
def view(account: Administrator, img_id=0) -> Response:
    for i in Incident.select().where(Incident.id == img_id):
        with open(i.image_path, 'rb') as image:
            return Response(image.read(), mimetype='image/jpeg')

    return Response('Not found', status=404)


@http.route('/login', methods=['GET', 'POST'])
def login():
    # Handle POST data
    if request.method == 'POST':
        username = escape(request.form.get('accountUsername'))
        password = escape(request.form.get('accountPassword'))
        if Account(username, password).login():
            session['account'] = {
                'username': username,
                'password': password
            }
            return redirect(url_for('dashboard'), code=302)
        else:
            return render_template("login.html", failed=True)
    else:
        return render_template("login.html", failed=False)


@http.route('/logout', methods=['GET'])
def logout() -> Response:
    session.pop('account', None)
    return redirect(url_for('login'), code=302)


if __name__ == '__main__':
    def run_bot():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(executor.start_polling(dp, skip_updates=True))
        loop.close()

    print('Starting telegram bot ...')
    t_bot = threading.Thread(target=run_bot)
    t_bot.start()

    print('Starting http server ...')
    http.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    )
