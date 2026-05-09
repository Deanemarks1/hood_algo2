import sqlite3
import pandas as pd
import os



#make sure your iphone is forwarding the text messages. 
#in settings. 


def read_in_text_messages ():
    
    # Connect to chat.db
    chat_db = os.path.expanduser('~/Library/Messages/chat.db')
    conn = sqlite3.connect(chat_db)
    
    # Query message data
    query = '''
    SELECT
        datetime(message.date/1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS full_datetime,
        handle.id AS other_party,
        message.is_from_me AS is_from_me,
        message.text
    FROM
        message
    LEFT JOIN handle ON message.handle_id = handle.ROWID
    ORDER BY message.date DESC
    LIMIT 1000
    '''
    
    df_raw = pd.read_sql_query(query, conn)
    
    # Parse date and time
    df_raw['date'] = pd.to_datetime(df_raw['full_datetime']).dt.date
    df_raw['time'] = pd.to_datetime(df_raw['full_datetime']).dt.time
    
    # Classify as 'sent' or 'received'
    df_raw['message_type'] = df_raw['is_from_me'].apply(lambda x: 'sent' if x == 1 else 'received')
    
    # Adjust other_party
    df_raw['other_party'] = df_raw.apply(lambda row: 'me' if row['message_type'] == 'sent' else row['other_party'], axis=1)
    
    # Final structure with rename
    df = df_raw[['date', 'time', 'text', 'other_party', 'message_type']].copy()
    df.rename(columns={'text': 'message'}, inplace=True)
    

    return df


