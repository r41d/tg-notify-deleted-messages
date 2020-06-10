import logging
import os
import pathlib
import sys

from telethon import TelegramClient, events
from helpers import load_env, get_on_new_message, get_on_message_deleted, cycled_clean_old_messages

BASE_DIR = (pathlib.Path(__file__).parent / '..').absolute()

# Configure logging level, based on the system environment variables
logging.basicConfig(level=os.getenv("LOGGING_LEVEL", logging.INFO))

# Loading environment variables
load_env(BASE_DIR)

# Configure logging level, based on the `.env` file and on the system environment variables
logging.basicConfig(level=os.getenv("LOGGING_LEVEL", logging.INFO))

if os.getenv("TELEGRAM_API_ID") is None or os.getenv("TELEGRAM_API_HASH") is None:
    logging.critical('Please, read `README.md` and set-up environment variables (you can create a copy of '
                     '`.env.example` file with new name `.env` and fill correct values')
    exit(1)


async def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'auth':
        # TODO: perform logout in the code, in case the user use `auth` argument
        logging.critical('You successfully authorized, please, run the same command without `auth` argument to '
                         'start monitoring your messages. If you want to log-out, remove the file `db/user.session`, '
                         'to log-out and re-execute this command')
        exit(0)

    if not await client.is_user_authorized():
        logger.critical('Please, execute `auth` command before starting the daemon (see `README.md` file)')
        exit(1)

    if bool(os.getenv('NOTIFY_ONGOING_MESSAGES', '1')):
        new_message_event = events.NewMessage()
    else:
        new_message_event = events.NewMessage(incoming=True, outgoing=False)

    client.add_event_handler(get_on_new_message(client), new_message_event)
    client.add_event_handler(get_on_message_deleted(client), events.MessageDeleted())

    await cycled_clean_old_messages()


with TelegramClient('db/user', os.getenv("TELEGRAM_API_ID"), os.getenv("TELEGRAM_API_HASH")) as client:
    client.loop.run_until_complete(main())
