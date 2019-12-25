from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json
import base64

engine = create_engine('sqlite:///foo.db')
Session = sessionmaker()
Base = declarative_base(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String)
    phone_number = Column(String)
    login = Column(String)
    password = Column(String)
    email = Column(String)

class Messages(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    book_id = Column(ForeignKey('books.id'))
    user_id = Column(ForeignKey('users.id'))

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    book_name = Column(String)
    description = Column(String)
    img = Column(String)
    user_id = Column(ForeignKey('users.id'))
    publishing_house = Column(String)
    author = Column(String)
    year = Column(Integer)
    ISBN = Column(String)
    series = Column(String)
    type_of_cover = Column(String)
    number_of_pages = Column(String)
    status = Column(String)
    language = Column(String)
    search = Column(String)

    @staticmethod
    def get_books():
        """Retrieve all users in the database."""
        book_list = Session(bind=engine).query(Book).all()
        book_dict = {}
        for u in book_list:
            path = 'knigodam/static/' + u.img
            image = open(path, 'rb')  # open binary file in read mode
            image_read = image.read()
            image_64_encode = base64.encodestring(image_read).decode('ascii')
            book = {'id': str(book.id), 'title': u.book_name,
                        'img' : image_64_encode}
            book_dict[str(u.id)] = book
        json.dumps(book_dict)
        return book_dict

    def get_book(self):
        """Retrieve an individual user from the database."""
        book = Session(bind=engine).query(Book).filter_by(id=self).first()
        if book is None:
            return 'There\'s no such book in our database.'
        path = 'knigodam/static/' + book.img
        image = open(path, 'rb')  # open binary file in read mode
        image_read = image.read()
        image_64_encode = base64.encodestring(image_read).decode('ascii')
        book_dict = {'id': str(book.id), 'title': str(book.book_name),
                     'description': book.description, 'img' : image_64_encode, 'user_id' : book.user_id}
        json.dumps(book_dict)
        return book_dict

    def simple_search(self):
        name = '%' + self + '%';
        book_list = Session(bind=engine).query(Book).filter(Book.book_name.like(name)).all();
        book_dict = []
        for u in book_list:
            path = 'knigodam/static/' + u.img
            image = open(path, 'rb')  # open binary file in read mode
            image_read = image.read()
            image_64_encode = base64.encodestring(image_read).decode('ascii')
            book = {'id': u.id, 'title': u.book_name,
                        'img' : image_64_encode}
           # book_dict[str(u.id)] = book
            book_dict.append(book)
        json.dumps(book_dict)
        return book_dict

    @staticmethod
    def edit_book(self_id, self_status):
        DBSession = Session(bind=engine)
        query = DBSession.query(Book).filter_by(id=self_id).update({Book.status: self_status},
                                                                   synchronize_session=False)
        DBSession.commit()
