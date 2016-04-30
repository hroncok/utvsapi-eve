from eve.auth import BasicAuth
from flask import request
from utvsapitoken import TokenClient


class BearerAuth(BasicAuth):
    '''
    Overrides Eve's built-in basic authorization scheme
    and uses utvsapitoken to validate bearer token
    '''
    def auth_logic(self, info, allowed_roles, resource, method):
        return 'cvut:utvs:general:read' in info['scope']

    def check_auth(self, token, allowed_roles, resource, method):
        c = TokenClient(check_token_uri='http://localhost:8080/token',
                        usermap_uri='http://localhost:8080/user')
        try:
            info = c.token_to_info(token)
        except:
            return False

        return self.auth_logic(info, allowed_roles, resource, method)

    def authorized(self, allowed_roles, resource, method):
        try:
            token = request.headers.get('Authorization').split(' ')[1]
        except:
            return False
        return self.check_auth(token, allowed_roles, resource, method)


class EnrollmentsAuth(BearerAuth):
    '''
    Overrides auth_logic for Enrollments
    '''
    def auth_logic(self, info, allowed_roles, resource, method):
        return 'cvut:utvs:enrollments:all' in info['scope']
