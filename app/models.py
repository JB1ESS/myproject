from app import db

class BjdCode(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    si = db.Column(db.String(10), nullable = True)
    gu = db.Column(db.String(10), nullable = True)
    dong = db.Column(db.String(10), nullable = False)
    bjdcode = db.Column(db.String(20), nullable = False)
    apartment = db.Column(db.String(100), nullable = False)

class AptDeal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bjdcode = db.Column(db.String(10), nullable = True)
    bjdong = db.Column(db.String(10), nullable = False)
    apartment = db.Column(db.String(100), nullable = False)
    buildyear = db.Column(db.String(10), nullable = False)
    dealyear = db.Column(db.String(10), nullable = False)  
    dealmonth = db.Column(db.String(10), nullable = False)
    dealday = db.Column(db.String(10), nullable = False)
    area = db.Column(db.String(10), nullable = False)
    floor = db.Column(db.String(10), nullable = False)
    price = db.Column(db.String(10), nullable = False)
      