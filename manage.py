
import unittest

from app import create_app

app = create_app(config_name=os.getenv('APP_SETTINGS'))

if __name__ == '__main__':
    test()
