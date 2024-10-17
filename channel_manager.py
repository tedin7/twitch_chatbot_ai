import json

def add_channel(channel_name):
    with open('channels.json', 'r+') as f:
        channels = json.load(f)
        if channel_name not in channels:
            channels.append(channel_name)
            f.seek(0)
            json.dump(channels, f)
            f.truncate()

def get_channels():
    with open('channels.json', 'r') as f:
        return json.load(f)
