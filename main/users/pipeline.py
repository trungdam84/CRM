from django.http import HttpResponseRedirect
from django.shortcuts import reverse
import urllib, string, random
from users.models import CustomUser

# This is initially from https://github.com/python-social-auth/social-core/blob/master/social_core/pipeline/user.py
def get_username(strategy, details, backend, user=None, *args, **kwargs):
    # Get the logged in user (if any)
    logged_in_user = strategy.storage.user.get_username(user)
    # print(details)

    # Custom: check for email being provided
    if not details.get('email'):
        error = "Sorry, but your social network (Facebook or Google) needs to provide us your email address."
        letters = string.ascii_letters

        while 1:
            email = ''.join(random.choice(letters) for i in range(25))
            user = CustomUser.objects.filter(email='{}@creatip.co.uk'.format(email))
            if not user:
                return {
                        'email': '{}@creatip.co.uk'.format(email),
                        }

  