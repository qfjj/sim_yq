from app import app
from flask_script import Manager

manage = Manager(app)

# 项目入口
if __name__ == "__main__":
    manage.run()
