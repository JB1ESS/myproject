from config.default import *

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'myweb.db'))#데이터베이스 접속주소
SQLALCHEMY_TRACK_MODIFICATIONS = False#SQLAlchemy 이벤트 처리옵션

SECRET_KEY = b'\x86\xee\x0f\xe6\x98B,\xbc\x0e\xbfpYX\xca8(' #CSRF 토큰 생성에 사용