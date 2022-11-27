import os

BASE_DIR = os.path.dirname(__file__) #현재 수행중인 코드를 담고있는 파일의 경로를 베이스 폴더로 지정

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'myweb.db'))#데이터베이스 접속주소
SQLALCHEMY_TRACK_MODIFICATIONS = False#SQLAlchemy 이벤트 처리옵션

SECRET_KEY = 'dev' #CSRF 토큰 생성에 사용