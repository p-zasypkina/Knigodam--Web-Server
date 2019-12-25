from knigodam.models import *
from pyramid.security import Allow, forget, remember
from pyramid.httpexceptions import HTTPFound
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.response import Response
from .security import groupfinder


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    with Configurator(settings=settings) as config:
        config.include('pyramid_jinja2')
        config.include('.routes')
        #config.add_view('.rest-api-books', route_name='rest_books')
        authn_policy = AuthTktAuthenticationPolicy(
        settings['knigodam.secret'], callback=groupfinder,
        hashalg='sha512')
        authz_policy = ACLAuthorizationPolicy()
        config.set_authentication_policy(authn_policy)
        config.set_authorization_policy(authz_policy)
        Base.metadata.create_all()
        config.scan()
    return config.make_wsgi_app()
