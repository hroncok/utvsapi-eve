from eve.auth import BasicAuth
from flask import request
from utvsapitoken import TokenClient


class BearerAuth(BasicAuth):
    '''
    Overrides Eve's built-in basic authorization scheme
    and uses utvsapitoken to validate bearer token
    '''

    def auth_logic(self, info, resource, method):
        return 'cvut:utvs:general:read' in info['scope']

    def check_auth(self, token, resource, method):
        c = TokenClient(check_token_uri='http://localhost:8080/token',
                        usermap_uri='http://localhost:8080/user')
        try:
            info = c.token_to_info(token)
        except:
            return False

        return self.auth_logic(info, resource, method)

    def authorized(self, allowed_roles, resource, method):
        try:
            token = request.headers.get('Authorization').split(' ')[1]
        except:
            return False
        return self.check_auth(token, resource, method)


class EnrollmentsAuth(BearerAuth):
    '''
    Overrides auth_logic for Enrollments
    '''

    def auth_logic(self, info, resource, method):
        if not super().auth_logic(info, resource, method):
            return False

        if 'cvut:utvs:enrollments:all' in info['scope']:
            return True

        if ('cvut:utvs:enrollments:by-role' in info['scope'] and
                'B-00000-ZAMESTNANEC' in info['roles']):
            return True

        if ('cvut:utvs:enrollments:personal' not in info['scope'] or
                'personal_number' not in info):
            return False

        # only see your enrollments, pretty easy:
        self.set_request_auth_value(info['personal_number'])
        return True
