from flask import request, redirect
from linkedin import linkedin


class LinkedInWrapper(object):
    def __init__(self, linkedin_key, linkedin_secret, callback_url):
        self.authentication = linkedin.LinkedInAuthentication(
            linkedin_key,
            linkedin_secret,
            callback_url,
            linkedin.PERMISSIONS.enums.values())

        self.application = linkedin.LinkedInApplication(self.authentication)

    def authorize(self):
        return redirect(self.authentication.authorization_url)

    def authorize_callback(self):
        if 'code' not in request.args:
            return None, None
        self.authentication.authorization_code = request.args['code']
        self.authentication.get_access_token()
        user = self.application.get_profile(selectors=['id', 'formatted-name'])
        return (
            'linkedin$' + user['id'],
            user.get('formattedName')
        )

    def get_companies_worked_at(self):
        positions = self.application.get_profile(selectors=['positions']).get('positions').get('values')
        companies = map(lambda position: position.get('company'), positions)
        unique_companies = []
        for cur_company in companies:
            if (cur_company.get('id') is not None
                    and len(filter(lambda company: cur_company.get('id') == company.get('id'), unique_companies)) == 0):
                unique_companies.append(cur_company)
        return unique_companies
