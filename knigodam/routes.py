def includeme(config):
    # web routes
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('books', '/books')
    config.add_route('book', '/books/{id}')
    config.add_route('book_delete', '/books/{id}/delete')

    config.add_route('user', '/user/{id}')
    config.add_route('news', '/news')
    config.add_route('managment', '/managment')
    config.add_route('about', '/about')
    config.add_route('register', '/register')
    config.add_route('auto', '/auto')
    config.add_route('logout', '/logout')
    config.add_route('login', '/login')
    config.add_route('chat', '/chat')
    config.add_route('hello', '/hello/{name}')
    config.add_route('autorization', '/autorization')
    config.add_route('code', '/code')
    config.add_route('publish', '/publish')
    config.add_route('search', '/search')
    # api routes
    config.add_route('rest_book', '/api/v1/books/{id:\d+}')
    config.add_route('rest_books', '/api/v1/books/')

    config.add_route('rest_simple_search', '/api/v1/search&entry={searchform}')




