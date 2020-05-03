import os
import copy
import json
import pandas as pd
import logging
import time
import datetime
import base64

from config import *


cache = {}


def list_chat_ids():
    return sorted(os.listdir(MSG_DIR))


def list_chat_titles(df):
    return sorted(df.title.unique().tolist())


def get_path_to_chat_json(chat_id):
    return os.path.join(MSG_DIR, chat_id, 'message_1.json')


def _load_messages(filename):
    if filename in cache:
        return cache[filename]
    else:
        with open(filename) as jsonfile:
            data = json.load(jsonfile)
            cache[filename] = data
            return data


def get_participants_from_chat_id(chat_id):
    filename = get_path_to_chat_json(chat_id)
    messages = _load_messages(filename)
    return [str(p['name'].encode('latin1').decode('utf8')) for p in messages['participants']]


def load_data():
    t0 = time.time()
    text_msgs = []
    photo_msgs = []

    for chat_id in list_chat_ids():
        filename = get_path_to_chat_json(chat_id)
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


def get_participants(df, title):
    chat_ids = df.loc[df.title == title].chat_id.tolist()
    participants = set()
    for chat in chat_ids:
        participants = participants.union(get_participants_from_chat_id(chat))
    return list(participants)


def filter_chat(df, chat_title):
    participants = get_participants(df, chat_title)
    return df.loc[(df.title == chat_title) & (df.sender_name.isin(participants))]


def read_image(filename):
    return base64.b64encode(open(filename, 'rb').read())
