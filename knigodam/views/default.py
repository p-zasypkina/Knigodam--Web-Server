from pyramid.view import view_config, view_defaults
from knigodam.models import *
from pyramid.security import Allow, forget, remember
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from ..security import *
import pyramid.httpexceptions as exc
import os
import uuid
import shutil
from sqlalchemy import func
import base64
import requests

# api
@view_config(route_name='rest_book', renderer='json')
def book_api(request):
    #DBSession = Session(bind=engine)
    #books = DBSession.query(Book).all()
    #return {'status': 'success'}
    if request.method == 'GET':
        id = request.matchdict['id']
        book = Book.get_book(id)
        return Response(str(book))

@view_config(route_name='rest_books', renderer='json')
def books_api(request):
    if request.method == 'GET':
        books = Book.get_books()
        return Response(str(books))




# web
@view_config(route_name='home', renderer='../templates/index.jinja2')
def my_view(request):
    #DBSession = Session(bind=engine)
    #id = request.matchdict['id']
   # books = DBSession.query(Book).get(id)
    #return {'title': books.id}
    like = ''
    message=''
    if 'like' in request.params:
        like = request.params['like']
    print(like)
    DBSession = Session(bind=engine)
    #books = DBSession.query(Book).all()
    #name = '%' + like.lower() + '%';
    name =  like.lower();
    #books = DBSession.query(Book).filter(Book.search.like(name)).all();
    books = DBSession.query(Book).all()
    print(books)
    #filter_add_books = filter(lambda x : name in x.search, books)
    #books = list(filter_add_books);
    filtered = []
    for book in books:
        if name in book.book_name.lower():
            filtered.append(book)

    if filtered == []:
        message='Ничего не найдено'
    #books = Book.simple_search(like)
    return {'books': filtered, 'logined': is_login(request), 'message':message}

@view_config(route_name='books', renderer='../templates/index.jinja2')
def books(request):
    return {}


@view_config(route_name='book', renderer='../templates/bookpage.jinja2')
def book(request):
    id = request.matchdict['id']
    DBSession = Session(bind=engine)
    book = DBSession.query(Book).get(id)
    #users = DBSession.query(UserBook).filter(UserBook.book_id == book.id)
    users = DBSession.query(User).filter(User.id == book.user_id)

    cookies = request.cookies
    if 'id' in cookies and request.method == 'POST':
        DBSession = Session(bind=engine)
        id = int(cookies['id'])
        new_message = Messages(text=request.params['message'], book_id=book.id, user_id = id)
        DBSession.add(new_message)
        DBSession.commit()

    show_form = True
    if not is_login(request):
        show_form=False
    else:
        id = int(cookies['id'])
        if id == book.user_id:
            show_form = False
    return {'book': book, 'users': users, 'logined': is_login(request), 'show_form': show_form}
'''
@view_config(route_name='book', renderer='../templates/bookpage.jinja2')
def message_seller(request):
    DBSession = Session(bind=engine)
    if request.method == 'POST':
        new_message = Messages(text=request.params['message'])
        DBSession.add(new_message)
    DBSession.commit()
    return {}

'''

@view_config(route_name='user', renderer='../templates/userpage.jinja2')
def user(request):
    id = request.matchdict['id']
    DBSession = Session(bind=engine)
    users = DBSession.query(User).get(id)
    books = DBSession.query(Book).filter(Book.user_id == users.id)
    return {'users': users, 'books': books}
    #return {'user': user, 'book':book}


@view_config(route_name='chat', renderer='../templates/chat.jinja2')
def chat(request):
    cookies = request.cookies
    message = ''
    if 'id' in cookies:
        DBSession = Session(bind=engine)
        id = int(cookies['id'])
        books = DBSession.query(Book).filter(Book.user_id == id)
        booksMessages = []
        no_message = ''
        message_count = 0
        for book in books:
            messages = DBSession.query(Messages).filter(Messages.book_id == book.id)
            bookMessages = []
            for message in messages:
                bookMessages.append({'id': message.id, 'text': message.text, 'user_id': message.user_id})
                message_count +=1
            booksMessages.append({'id': book.id, 'name': book.book_name, 'messages': bookMessages, 'img':book.img})
        if message_count==0:
            no_message = 'У вас нет сообщений'
        return {'data': booksMessages, 'logined': is_login(request),'no_message': no_message}


    else:
        raise exc.HTTPFound(request.route_url("login", _query={'came_from':'chat'}))


@view_config(route_name='news', renderer='../templates/news.jinja2')
def news(request):
    return {}

def is_login(request):
    cookies = request.cookies
    if 'login' in cookies and 'id' in cookies:
        return True
    return False

@view_config(route_name='managment', renderer='../templates/managment.jinja2')
def managment(request):
    #DBSession = Session(bind=engine)
    #new_user = User(name="Vasya")
    #DBSession.add(new_user)
    #DBSession.commit()
    #if True:
    #    response = Response('Failed validation: ')
    #    response.status_int = 500
     #   return response
    message =''
    cookies = request.cookies
    if 'login' not in cookies:
        raise exc.HTTPFound(request.route_url("login"))
    else:
        if cookies ["login"] == '':
            raise exc.HTTPFound(request.route_url("login"))

    if 'id' in cookies:
        if request.method == 'POST':
            book_id = request.params['book_id']
            status = request.POST['status']
            Book.edit_book(book_id, status)

        id = int(cookies['id'])
        DBSession = Session(bind=engine)
        books = DBSession.query(Book).filter(Book.user_id == id).all();

        if len(books) == 0:
            message = 'Вы еще не разместили книги';


        #new_status = Book(status = request.params['status'])
        #DBSession.add(new_status)
        #DBSession.commit()
        return {'books': books, 'logined': is_login(request), 'message':message}
    else:
        raise exc.HTTPFound(request.route_url("login"))


@view_config(route_name='auto', renderer='../templates/login.jinja2')
def auto(request):
    return {}

@view_config(route_name='register', renderer='../templates/register.jinja2')
def register(request):
    DBSession = Session(bind=engine)
    if request.method == 'POST':
        pass_hash = hash_password(request.params['pass'])
        new_user = User(name=request.params['name'],city=request.params['town'], phone_number=request.params['tel'],
                        email=request.params['email'],login=request.params['name'],password=pass_hash)
        DBSession.add(new_user)
    DBSession.commit()
    return {'logined': is_login(request)}

@view_config(route_name='login', renderer='../templates/login.jinja2')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
       referrer = '/'  # never use login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    page = ''
    if 'page' in request.params:
        page = request.params['page']
    if request.method == 'POST':
        login = request.params['login']
        password = request.params['password']
        #page = request.params['page']
        DBSession = Session(bind=engine)
        user = DBSession.query(User).filter(
          User.login == login
        ).first()

        if user and check_password(password, user.password):
            headers = remember(request, login)
            #if page =='chat':
               # came_from =
            response = HTTPFound(location=came_from,
                            headers=headers)
            response.set_cookie('login', value=login, max_age=31536000) # max_age = year
            response.set_cookie('id', value=str(user.id), max_age=31536000)
            return response

        message = 'Failed login'

    return {
        'name': 'Login',
        'message': message,
        'url': request.application_url + '/login',
        'came_from': came_from,
        'login': login,
        'password': password,
        'page': page
    }

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    url = request.route_url('home')
    response = HTTPFound(location=url,
                     headers=headers)
    response.set_cookie('login', value=None, max_age=31536000)  # max_age = year
    response.set_cookie('id', value=None, max_age=31536000)
    return response

@view_config(route_name='autorization', renderer='../templates/autorization.jinja2')
def autorization(request):
    return {}

@view_config(route_name='code', renderer='../templates/code.jinja2')
def code(request):
    return {}

@view_config(route_name='publish', renderer='../templates/publish.jinja2')
def publish(request):
    cookies = request.cookies
    if not is_login(request):
        raise exc.HTTPFound(request.route_url("login"))
    if request.method == 'POST':
        file_name = '%s.jpeg' % uuid.uuid4()
        input_file = request.POST['cover'].file
        #print(os.path.realpath(__file__))

        full_path = os.path.dirname(os.path.relpath(__file__)).replace('views', 'static/')+file_name
        print(full_path)
        # Finally write the data to a temporary file
        input_file.seek(0)
        with open(full_path, 'wb') as output_file:
            shutil.copyfileobj(input_file, output_file)
        DBSession = Session(bind=engine)
        id = int(cookies['id'])
        new_book = Book(book_name=request.params['title'], description=request.params['des'],
                        img=file_name, publishing_house=request.params['publishing_house'],
                        author=request.params['author'], year=request.params['year'], ISBN=request.params['isbn'],
                        series=request.params['series'], type_of_cover=request.params['type_obl'],
                        number_of_pages=request.params['kol'], language=request.params['language'], user_id=id, status='Не куплена',
                        search=request.params['title'].lower()+" "+request.params['des'].lower())
        DBSession.add(new_book)
        DBSession.commit()
    return {'logined': is_login(request)}

@view_config(route_name='book_delete')
def delete(request):
    id = request.matchdict['id']
    DBSession = Session(bind=engine)
    books = DBSession.query(Book).filter(Book.id == id).delete()
    DBSession.commit()
    url = request.route_url('managment')
    return HTTPFound(location=url)


'''
@view_config(route_name='search')
def search(request):
    DBSession = Session(bind=engine)
    if request.method=='GET':
        #books_searche = DBSession.execute("SELECT name FROM Book WHERE name LIKE '%Python%'")
        books_searche = DBSession.execute("SELECT * FROM books")
        data = books_searche.fetchall()
        print(data)
    DBSession.commit()
    return {'search': data}
    
@view_config(route_name='search')
def show_book(self ):
    DBSession = Session(bind=engine)
    name = '%' + self + '%';
    book_list = Session(bind=engine).query(Book).filter(Book.book_name.like(name)).all();
    DBSession.commit()
    return { 'book_list':book_list}
    
    @view_config(route_name='rest_simple_search', renderer='../templates/search.jinja2')
def books_api(request):
    if request.method == 'GET':
        search_string = request.matchdict['searchform']
        books = Book.simple_search(search_string)
        return Response(str(books))
@view_config(route_name='register', renderer='../templates/register.jinja2')
def register(request):
    DBSession = Session(bind=engine)
    if request.method == 'POST':
        pass_hash = hash_password(request.params['pass'])
        new_user = User(name=request.params['name'],city=request.params['town'], phone_number=request.params['tel'],
                        email=request.params['email'],login=request.params['name'],password=pass_hash)
        DBSession.add(new_user)
    DBSession.commit()
    return {'logined': is_login(request)}
'''






@view_config(route_name='search', renderer='../templates/search.jinja2')
def search(request):
    DBSession = Session(bind=engine)
    query = DBSession.query(Book);
    message =''
    if 'title' in request.params and request.params['title'] != '':
        title = request.params['title']
        print(title)
        query = DBSession.query(Book).filter(Book.book_name.like('%' + title + '%'));

    if 'publishing_house' in request.params and request.params['publishing_house'] != '':
        publishing_house = request.params['publishing_house']
        query=query.filter(Book.publishing_house.like('%' + publishing_house + '%'))

    if 'author' in request.params and request.params['author'] != '':
        author = request.params['author']
        query=query.filter(Book.author.like('%' + author + '%'))

    if 'year' in request.params and request.params['year'] != '':
        year = request.params['year']
        query=query.filter(Book.year.like('%' + year + '%'))

    if 'isbn' in request.params and request.params['isbn'] != '':
        isbn = request.params['isbn']
        query=query.filter(Book.ISBN.like('%' + isbn + '%'))

    if 'town' in request.params and request.params['town'] != '':
        town = request.params['town']
        users = DBSession.query(User).filter(User.city.like('%' + town + '%')).all();
        usersIds = list(map(lambda x: x.id, users))
        print(usersIds)
        query=query.filter(Book.user_id.in_(usersIds))
    books = query.all();
    if len(books) == 0:
        message = 'Ничего не найдено'

    return {
        'books': books,
        'logined': is_login(request),
        'message': message
    }



