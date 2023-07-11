from allauth.socialaccount.models import SocialApp
import requests
from django.utils import timezone

def refresh_token(user):
    try:
        social_account = user.socialaccount_set.get(provider='google')
    except:
        return False

    social_token = social_account.socialtoken_set.first()
    
    # Check to see if the token has expired. 
    # If not, return early
    if social_token.expires_at < timezone.now():
        return False
    
    app = SocialApp.objects.get(provider=social_account.provider)
    
    # Google's token endpoint
    token_url = "https://oauth2.googleapis.com/token"
    
    # Prepare the refresh token data
    refresh_data = {
        "client_id": app.client_id,
        "client_secret": app.secret,
        "grant_type": "refresh_token",
        "refresh_token": social_token.token_secret,
    }

    # Make the request
    response = requests.post(token_url, data=refresh_data)
    
    if response.status_code == 200:
        response_data = response.json()

        # Update the token
        social_token.token = response_data["access_token"]
        social_token.save()
        return True

    return False

