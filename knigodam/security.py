import bcrypt
from knigodam.models import Session, User

def hash_password(pw):
    pwhash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
    return pwhash.decode('utf8')

def check_password(pw, hashed_pw):
    expected_hash = hashed_pw.encode('utf8')
    return bcrypt.checkpw(pw.encode('utf8'), expected_hash)

def groupfinder(login, request):
    DBSession = Session(bind=engine)
    user = DBSession.query(User).filter(
      User.login == login and User.password == request.params['password']
    ).first()
    if user:
        return ['group:editors']
    return []