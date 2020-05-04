import os
import copy
import json
import pandas as pd
import logging
import time
import datetime
import base64

from config import *

# helper functions


def _load_messages(filename):
    with open(filename) as jsonfile:
        data = json.load(jsonfile)
        return data


def _get_path_to_chat_json(chat_id):
    return os.path.join(MSG_DIR, chat_id, 'message_1.json')


def _list_chat_ids():
    return sorted(os.listdir(MSG_DIR))


# dataload

def load_data():
    t0 = time.time()
    text_msgs = []
    photo_msgs = []

    for chat_id in _list_chat_ids():
        filename = _get_path_to_chat_json(chat_id)
        data = _load_messages(filename)
        title = data['title'].encode('latin1').decode('utf8')
        for msg in data['messages']:
            if 'content' in msg.keys():
                text_msgs.append(
                    {
                        'chat_id': chat_id,
                        'title': title,
                        'timestamp': msg['timestamp_ms'],
                        'sender_name': msg['sender_name'].encode('latin1').decode('utf8'),
                        'content': msg['content'].encode('latin1').decode('utf8'),
                    }
                )
            if 'photos' in msg.keys():
                for item in msg.get('photos'):
                    photo_msgs.append(
                        {
                            'chat_id': chat_id,
                            'title': title,
                            'timestamp': msg['timestamp_ms'],
                            'sender_name': msg['sender_name'].encode('latin1').decode('utf8'),
                            'photo_uri': os.path.join(DATA_DIR, item['uri']),
                            'photo_creation_timestamp': item['creation_timestamp']
                        }
                    )

    df = pd.DataFrame(text_msgs)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    df_photos = pd.DataFrame(photo_msgs)
    df_photos['timestamp'] = pd.to_datetime(df_photos['timestamp'], unit='ms')
    df_photos['photo_creation_timestamp'] = pd.to_datetime(
        df_photos['photo_creation_timestamp'], unit='ms')

    logging.info(f'Loading all data took {time.time()-t0:.4f} seconds.')
    return df, df_photos


def read_image(filename):
    return base64.b64encode(open(filename, 'rb').read())
