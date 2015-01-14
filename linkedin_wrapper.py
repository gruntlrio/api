from flask import request, redirect
from linkedin import linkedin


class LinkedInWrapper(object):
    def __init__(self, linkedin_key, linkedin_secret, callback_url, token=None):
        self.authentication = None
        self.application = None
        self.token = None

        if token is None:
            self.authentication = linkedin.LinkedInAuthentication(
                linkedin_key,
                linkedin_secret,
                callback_url,
                linkedin.PERMISSIONS.enums.values())
        else:
            self.application = linkedin.LinkedInApplication(token=token)
            self.token = token

    def authorize(self):
        return redirect(self.authentication.authorization_url)

    def authorize_callback(self):
        if 'code' not in request.args:
            return None, None
        self.authentication.authorization_code = request.args['code']
        self.authentication.get_access_token()
        self.token = self.authentication.token[0]
        self.application = linkedin.LinkedInApplication(self.authentication)

    def get_token(self):
        return self.token

    def get_profile(self):
        if self.application is None:
            raise LinkedInUnauthorized()

        try:
            user = self.application.get_profile(selectors=['id', 'formatted-name'])
        except linkedin.LinkedInError:
            raise LinkedInUnauthorized()

        return (
            'linkedin$' + user['id'],
            user.get('formattedName')
        )

    def get_companies_worked_at(self):
        if self.application is None:
            raise LinkedInUnauthorized()

        try:
            positions = self.application.get_profile(selectors=['positions']).get('positions').get('values')
        except linkedin.LinkedInError:
            raise LinkedInUnauthorized()

        companies = map(lambda position: position.get('company'), positions)
        unique_companies = []
        for cur_company in companies:
            if (cur_company.get('id') is not None
                    and len(filter(lambda company: cur_company.get('id') == company.get('id'), unique_companies)) == 0):
                unique_companies.append(cur_company)
        return unique_companies


class LinkedInUnauthorized(Exception):
    def __init__(self):
        pass