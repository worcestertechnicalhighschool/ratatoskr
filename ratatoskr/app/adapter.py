# from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.http import HttpResponse

class RatatoskrAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        You can use this hook to intervene, e.g. abort the login by
        raising an ImmediateHttpResponse

        Why both an adapter hook and the signal? Intervening in
        e.g. the flow from within a signal handler is bad -- multiple
        handlers may be active and are executed in undetermined order.
        """

        # Retrieve the username and domain for logic below
        username = sociallogin.user.email.split('@')[0]
        domain = sociallogin.user.email.split('@')[1]

        # Authorized domains only
        if domain != "worcesterschools.net" and domain != "techhigh.us":
            # Students are restricted. all student emails begin with 'student.'
            raise ImmediateHttpResponse(HttpResponse('Sorry, you are not allowed'))
        
        # No Students allowed
        if domain == "worcesterschools.net" and username.startswith('student.'):
            raise ImmediateHttpResponse(HttpResponse('Sorry, you are not allowed'))

        pass
