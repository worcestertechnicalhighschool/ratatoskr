from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied
# from allauth.exceptions import ImmediateHttpResponse

class RatatoskrAccountAdapter(DefaultSocialAccountAdapter):
    def authentication_error(self, request, provider_id, error, exception, extra_context):
        print(error)

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
            raise PermissionDenied()
        
        # No Students allowed
        if domain == "worcesterschools.net" and username.startswith('student.'):
            raise PermissionDenied()

        pass
