# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

#Documentation
#http://127.0.0.1:8000/docs/

# Create your tests here.

#url to run top 4 for all pages
#http://127.0.0.1:8000/wiser/GetTopContributors/?top=4
#Return status = 200


#case to handle when top > available users
##http://127.0.0.1:8000/wiser/GetTopContributors/?top=1000
#Return status = 406

#case to handle when top <=0
##http://127.0.0.1:8000/wiser/GetTopContributors/?top=-1
#Return status = 406


#case to handle when curr_page > last page
##http://127.0.0.1:8000/wiser/GetTopContributors/?top=-1&curr_page=8
#Return status = 406

# One of GitHub repo returns 204:No Content
# Have handled that case too.

#default case top =3 cp = 3
# http://127.0.0.1:8000/wiser/GetTopContributors/

#Added error handling on Pagination when max_page does not exist

#In wiser_app/views.py, toggle between incorrect and correct "Access" and then run http://127.0.0.1:8000/wiser/GetTopContributors/
#Handled the case for incorrect login or ratelimit exceeding

#In wiser_app/views.py, toggle between incorrect and correct "org" and then run http://127.0.0.1:8000/wiser/GetTopContributors/
#Handled the case to handle bad org request
