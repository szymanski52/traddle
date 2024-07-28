import json


def load_config():
    with open('config.json') as f:
        return json.load(f)


class Config:
    def __init__(self):
        self.data = load_config()

    def get_db_dsn(self):
        return self.data['db']['dsn']

    def get_predict_cron(self):
        return self.data['predict']['cron']


config = Config()
