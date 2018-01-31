# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
# from github import Github
from rest_framework import mixins
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
import urllib2
import json
from sets import Set
from operator import itemgetter
import requests
import re
import time

# Create your views here.
#Constant Values

Access = 'a4261ce71d7a6a4cfaec782618ecf11e46948d28'#correct
# Access = 'a4261ce71d7a6a4cfaec782618ecf11e46948d2'#incorrect

org = 'github'#correct
# org = 'githb'#incorrect

head = {'Authorization': 'token {}'.format(Access)}
curr_page = 1

#GitHubAPI's per_page max
per_page = 100
base_uri = 'https://api.github.com/orgs/' + str(org) + '/repos?&page=1&per_page=' + str(per_page)
uri = 'https://api.github.com/orgs/' + str(org) + '/repos?&page=' + str(curr_page) + '&per_page=' + str(per_page)


def getPageNumber(link, index):
  '''
  	**Function to search and parse for page numbers in the link header
  	'''
  temp = 0
  # Relying on GitHub's header format
  while link != '\n' and link[int(index) + int(temp)] != '&':
    temp += 1
  page = link[index:index + temp]
  return page


def getPageLimit(base_uri):
  '''
  	**Function to Page information to handle pagination
  	Input :base uri
  	Output:Array which contains the first page and last page
  	Assumptions: GithubAPI follows proper header format. GitHubAPI limits calls to 300 users.per_page=100(max)
  	No error checking done on GitHubAPI's header.
  	'''
  page_limit = []
  req = requests.get(base_uri, headers=head)
  if (req.status_code == status.HTTP_200_OK):
    pagination_link = req.headers.get('link', None)
    if pagination_link is not None:
      data = [m.start() for m in re.finditer('page', pagination_link)]
      if len(data) == 4 and data.count is not None:
        first_occurence = data[0] + 5
        third_occurence = data[2] + 5
        next_page = getPageNumber(pagination_link, first_occurence)
        last_page = getPageNumber(pagination_link, third_occurence)
        page_limit.append(next_page)
        page_limit.append(last_page)
  else:
    page_limit is None
  
  return page_limit


def jsonReader(uri):
  '''
  	**Function to instantiate the GitHub with AccessToken
  	Input : uri
  	Output : json object
  	'''
  r = requests.get(uri, headers=head)
  if (r.status_code is status.HTTP_200_OK):
    data = r.json()
  elif (r.status_code is status.HTTP_403_FORBIDDEN):
    data = None
    # return Response("Wrong Access Token or requests > APILimit(5k)", status=status.HTTP_403_FORBIDDEN)
  else:
    data = None
  return data


def repoFromOrg(uri):
  '''
  	**Function that queries all the repo from the Org
  	Input : uri
  	Output: Set with the 'name' field
  	'''
  name_list = Set()
  getPageLimit(uri)
  data = jsonReader(uri)
  if data is not None:
    datalen = len(data)
    for obj in range(datalen):
      obName = data[obj].get('name')
      name_list.add(obName)
  else:
    name_list is None
  return name_list


class GetRepoList(APIView):
  '''
  	**API that retrieves the list of all Repo for a particular org**
  	Request Parameters: None

  	'''
  def get(self, request):
    orgrepolist = Set()
    current_page = 1
    page_array = getPageLimit(base_uri)
    page_array_len = len(page_array)
    if (page_array_len != 0):
      last_page = page_array[1]
    else:
      return Response("Wrong Access Token/requests > APILimit(5k)/org not present", status=status.HTTP_401_UNAUTHORIZED)
    while int(current_page) <= int(last_page):
      print(current_page)
      uri_org_repo = 'https://api.github.com/orgs/' + str(org) + '/repos?&page=' + \
                     str(current_page) + '&per_page=' + str(per_page)
      orgrepolist = repoFromOrg(uri_org_repo)
      current_page = current_page + 1
    
    if orgrepolist is not None:
      return Response(orgrepolist, status=status.HTTP_200_OK)
    else:
      return Response("NO CONTENT", status=status.HTTP_204_NO_CONTENT)


class GetTopContributors(APIView):
  '''
  	**API that retrieves the list of Top Contributors for all repo committed to a particular organization**
  	Request Parameters: (1)top(default = 3) (2)curr_page (default = 3)
  	'''
  def get(self, request):
    start_time = time.time()
    print('Starting...')
    # current_page = 3
    top = self.request.query_params.get('top', 3)
    print ('top', top)
    if int(top) <= 0:
      return Response('Top cannot be zero or negative',
                      status=status.HTTP_406_NOT_ACCEPTABLE)
    current_page = int(self.request.query_params.get('curr_page', 3))
    print ('cp', current_page)
    github_name_contrib = dict()
    page_array = getPageLimit(base_uri)
    page_array_len = len(page_array)
    if (page_array_len != 0):
      last_page = page_array[1]
    else:
      return Response("Wrong Access Token/requests > APILimit(5k)/org not present", status=status.HTTP_400_BAD_REQUEST)
    if int(current_page) > int(last_page):
      return Response('CurrentPage specified is more than LastPage. LastPage = '+str(last_page),status = status.HTTP_406_NOT_ACCEPTABLE)
    while int(current_page) <= int(last_page):
      contrib_uri = 'https://api.github.com/orgs/' + str(org) + '/repos?&page=' + str(
        current_page) + '&per_page=' + str(per_page)
      orgrepolist = repoFromOrg(contrib_uri)
      if orgrepolist is None:
        return Response("NO CONTENT", status=status.HTTP_204_NO_CONTENT)
      else:
        for contrib in orgrepolist:
          uriforcont = 'https://api.github.com/repos/' + str(org) + '/' + str(contrib) + '/contributors'
          data_contrib = jsonReader(uriforcont)
          if data_contrib is not None:
            datalen_contrib = len(data_contrib)
            for obj in range(datalen_contrib):
              login = data_contrib[obj].get('login')
              contributions = data_contrib[obj].get('contributions')
              if not login in github_name_contrib:
                github_name_contrib[login] = contributions
              else:
                github_name_contrib[login] += contributions
        current_page = current_page + 1
    sorted_contributors = sorted(github_name_contrib.items(), key=itemgetter(1), reverse=True)
    sortedlen = len(sorted_contributors)
    if int(top) > sortedlen:
      print("--- %s seconds ---" % (time.time() - start_time))
      return Response(sorted_contributors[:int(top)], status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)
    else:
      print('Successful Completion')
      print("--- %s seconds ---" % (time.time() - start_time))
      # return Response(str(sorted_contributors[:int(top)]) + " Time(in secs) = " + str(time.time() - start_time), status=status.HTTP_200_OK)
      return Response(sorted_contributors[:int(top)], status=status.HTTP_200_OK)



