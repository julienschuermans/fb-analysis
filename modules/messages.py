import string
import time
import os
import logging
import numpy as np
import math
from collections import Counter

import nltk
from nltk import sent_tokenize, word_tokenize, PorterStemmer
from nltk.corpus import stopwords

import pandas as pd
from pandas.api.types import CategoricalDtype

from config import BORING_WORDS, MY_NAME, MSG_DIR

words_to_ignore = set(stopwords.words('english')).union(
    stopwords.words('dutch')).union(BORING_WORDS).union(set([x for x in string.digits + string.punctuation + string.whitespace + string.hexdigits + string.octdigits]))


# basic stuff

def list_chat_titles(df):
    return sorted(df.title.unique().tolist())


def list_contacts(df):
    return sorted(df.sender_name.unique().tolist())


def filter_df_on_title(df, chat_title):
    return df.loc[df.title == chat_title]


# Global analysis


def get_msg_count_in_out(df, granularity):

    sent = df.loc[df.sender_name == MY_NAME]
    received = df.loc[df.sender_name != MY_NAME]

    if granularity == 'Hourly':
        s = sent.groupby(pd.Grouper(key='timestamp', freq='H')).size(
        ).reset_index().rename(columns={0: 'msg_count'})
        r = received.groupby(pd.Grouper(key='timestamp', freq='H')).size(
        ).reset_index().rename(columns={0: 'msg_count'})

    elif granularity == 'Daily':
        s = sent.groupby(pd.Grouper(key='timestamp', freq='D')).size(
        ).reset_index().rename(columns={0: 'msg_count'})
        r = received.groupby(pd.Grouper(key='timestamp', freq='D')).size(
        ).reset_index().rename(columns={0: 'msg_count'})

    elif granularity == 'Monthly':
        s = sent.groupby(pd.Grouper(key='timestamp', freq='MS')).size(
        ).reset_index().rename(columns={0: 'msg_count'})
        r = received.groupby(pd.Grouper(key='timestamp', freq='MS')).size(
        ).reset_index().rename(columns={0: 'msg_count'})

    elif granularity == 'Yearly':
        s = sent.groupby(pd.Grouper(key='timestamp', freq='YS')).size(
        ).reset_index().rename(columns={0: 'msg_count'})
        r = received.groupby(pd.Grouper(key='timestamp', freq='YS')).size(
        ).reset_index().rename(columns={0: 'msg_count'})
    else:
        raise NotImplementedError()

    s['type'] = 'sent'
    r['type'] = 'received'

    results = s.append(r)

    return results


def get_weekly_activity_pattern(df):
    selected = df.loc[df.sender_name == MY_NAME]

    days = ['Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday']
    cat_type = CategoricalDtype(categories=days, ordered=True)
    weekdays = selected['timestamp'].dt.day_name().astype(cat_type)

    hours = range(24)
    cat_type = CategoricalDtype(categories=hours, ordered=True)
    day_hours = selected['timestamp'].dt.hour.astype(cat_type)

    result = selected.groupby([weekdays, day_hours]).size().unstack(level=0)

    return result


def get_total_msg_count_per_contact(df):
    """Returns the number of messages sent by every contact"""

    result = df.groupby('sender_name').size().reset_index().rename(
        columns={0: 'msg_count'}).sort_values(by='msg_count', ascending=False)

    my_count = result.loc[result.sender_name == MY_NAME].msg_count.tolist()[0]
    others = result.loc[result.sender_name != MY_NAME]

    return dict(mine=my_count,
                theirs=(others.sender_name.tolist(), others.msg_count.tolist())
                )


# Analysis per chat

def get_msg_count_per_contact(df, granularity):
    """ Returns the number of messages sent per user within a predefined interval """

    if granularity == 'Hourly':
        return df.groupby(by=[pd.Grouper(key='timestamp', freq='H'), 'sender_name']).size().reset_index().rename(columns={0: 'msg_count'})
    elif granularity == 'Daily':
        return df.groupby(by=[pd.Grouper(key='timestamp', freq='D'), 'sender_name']).size().reset_index().rename(columns={0: 'msg_count'})
    elif granularity == 'Monthly':
        return df.groupby(by=[pd.Grouper(key='timestamp', freq='MS'), 'sender_name']).size().reset_index().rename(columns={0: 'msg_count'})
    elif granularity == 'Yearly':
        return df.groupby(by=[pd.Grouper(key='timestamp', freq='YS'), 'sender_name']).size().reset_index().rename(columns={0: 'msg_count'})
    else:
        raise NotImplementedError


def get_msg_distribution_per_contact(df, timeframe):
    """Returns the total nb of messages sent per day of the week, or per hour of the day"""

    if timeframe == 'Day of Week':
        days = ['Monday', 'Tuesday', 'Wednesday',
                'Thursday', 'Friday', 'Saturday', 'Sunday']
        cat_type = CategoricalDtype(categories=days, ordered=True)
        weekdays = df['timestamp'].dt.day_name().astype(cat_type)
        result = df.groupby([weekdays, 'sender_name']).size(
        ).reset_index().rename(columns={0: 'msg_count'})
        return result

    elif timeframe == 'Hour of Day':
        hours = range(24)
        cat_type = CategoricalDtype(categories=hours, ordered=True)
        day_hours = df['timestamp'].dt.hour.astype(cat_type)
        return df.groupby([day_hours, 'sender_name']).size().reset_index().rename(columns={0: 'msg_count'})
    else:
        raise NotImplementedError


def get_wordcount(df):
    "returns the word count of all messages in this df, sorted by descending frequency"

    results = Counter()
    text = df['content'].str.lower().dropna().apply(
        nltk.word_tokenize).apply(' '.join)
    counted = Counter(" ".join(text.values.tolist()).split(" ")).items()
    filtered = {
        x: y for x, y in counted if not x in words_to_ignore}
    result = sorted([(k, v) for k, v in filtered.items()],
                    key=lambda item: item[1], reverse=True)
    return result

# Contact analysis


def _tokenize_all_content(df):
    return list(set(nltk.word_tokenize(' '.join(df['content'].str.lower().dropna().values.tolist()))).difference(words_to_ignore))


def _avg_words_per_message(df):
    return np.mean([len(x) for x in df['content'].str.lower().dropna().apply(nltk.word_tokenize).values.tolist()])


def get_contact_stats(df, selected_contacts):

    selection = df.loc[df.sender_name.isin(selected_contacts)]
    grouper = selection.groupby('sender_name')
    stats = grouper.size().reset_index().rename(
        columns={'sender_name': 'Name', 0: 'Message Count'})

    tokenized = grouper.apply(_tokenize_all_content)

    stats['Vocab. size'] = tokenized.apply(set).apply(len).values
    stats['Avg. word length'] = tokenized.apply(
        lambda words: np.mean([len(word) for word in words])).values
    stats['Avg. words per msg'] = grouper.apply(
        _avg_words_per_message).values

    return stats


def get_weighted_adjacency_matrix(df):

    msgs_per_sender_per_title = df.groupby(['sender_name', 'title']).size(
    ).reset_index().rename(columns={0: 'msg_count'})

    receivers_per_title = df[['title', 'sender_name']].rename(
        columns={'sender_name': 'receiver_name'})

    combined = msgs_per_sender_per_title.merge(receivers_per_title, on='title')
    combined = combined[combined['sender_name'] !=
                        combined['receiver_name']].drop_duplicates().drop(columns='title')

    connectivity = combined.groupby(['sender_name', 'receiver_name'])[
        'msg_count'].sum().unstack()

    return connectivity.columns.tolist(), connectivity.values
