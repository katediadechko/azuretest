
from atconfig import *
from attypes import *

import json
import base64
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import re

class RestClientError(Exception):
  pass

class RestClient:
  _connectTimeout = 5
  _readTimeout = 120

  def __init__(self, baseUri, accessToken):
    baseUri.rstrip('/')
    self._baseUri = baseUri + '/_apis'
    self.__session = requests.Session()
    retry = Retry(connect = 3, backoff_factor = 0.5)
    adapter = HTTPAdapter(max_retries = retry)
    self.__session.mount('http://', adapter)
    self.__session.mount('https://', adapter)
    accessToken += ':'
    tokenBase64 = b'Basic ' + base64.b64encode(accessToken.encode("utf8"))
    self.__session.headers.update({'Authorization': tokenBase64})

  def _get(self, uri, cont):
    res = []
    contToken = ''
    while True:
      contUri = uri + f'?$top=200&continuationtoken={contToken}' if cont == True else uri
      response = self.__session.get(contUri, timeout = (self._connectTimeout, self._readTimeout))
      response.raise_for_status()

      try:
        json = response.json()
        res.append(json)
      except ValueError:
        raise RestClientError(f'Failed to convert response to JSON: {response.text}')

      if cont == True and 'x-ms-continuationtoken' in response.headers:
        contToken = response.headers['x-ms-continuationtoken']
      else:
        break
    return res

class TestPlan(RestClient):
  def __init__(self, projectUri, accessToken, testPlanId):
    RestClient.__init__(self, projectUri, accessToken)
    self.__testPlanId = testPlanId
    self.__listConfigs()
    self.__listSuites()
    self.__testCases = []
    self.__testPoints = []
    self.__testTags = []
    tags = set()
    for suite in self.__testSuites:
      suiteTestCases = self.__listCasesInSuite(suite.id)
      for case in suiteTestCases:
        # store unique test case records
        if not any(tc.id == case.id for tc in self.__testCases):
          self.__testCases.append(case)
        for tag in case.tags:
          tags.add(tag)
      self.__testTags = sorted(list(tags))
      suiteTestPoints = self.__listPointsInSuite(suite.id)
      for point in suiteTestPoints:
        # test point records are always unique
        self.__testPoints.append(point)

  def __getWorkitem(self, id):
    uri = f'{self._baseUri}/wit/workitems/?ids={id}'
    widata = self._get(uri, False)[0]['value'][0]
    wi = Workitem(
      widata['id'],
      widata['rev'],
      widata['fields']['System.Description'] if 'System.Description' in widata['fields'] else '',
      widata['fields']['System.Tags'] if 'System.Tags' in widata['fields'] else '')
    return wi

  def __listSuites(self):
    print(f'Listing test suites')
    uri = f'{self._baseUri}/testplan/Plans/{self.__testPlanId}/Suites'
    jsons = self._get(uri, True)
    self.__testSuites = []
    for json in jsons:
      for suiteData in json['value']:
        workitem = self.__getWorkitem(suiteData['id'])
        self.__testSuites.append(
          TestSuite(
            suiteData['id'],
            suiteData['name'],
            workitem.desc,
            TestSuiteType[suiteData['suiteType']],
            suiteData['parentSuite']['id'] if 'parentSuite' in suiteData else None))

  def __listCasesInSuite(self, suiteId):
    print(f'Listing test cases in test suite {suiteId}')
    uri = f'{self._baseUri}/testplan/Plans/{self.__testPlanId}/Suites/{suiteId}/TestCase'
    jsons = self._get(uri, True)
    cases = []
    for json in jsons:
      for caseData in json['value']:
        workitem = self.__getWorkitem(caseData['workItem']['id'])
        cases.append(
          TestCase(
            caseData['workItem']['id'],
            caseData['workItem']['name'],
            workitem.desc,
            re.split('; ', workitem.tags),
            None))
    return cases

  def __listPointsInSuite(self, suiteId):
    print(f'Listing test points in test suite {suiteId}')
    uri = f'{self._baseUri}/testplan/Plans/{self.__testPlanId}/Suites/{suiteId}/TestPoint'
    jsons = self._get(uri, True)
    points = []
    for json in jsons:
      for pointData in json['value']:
        points.append(
          TestPoint(
            pointData['id'],
            pointData['testSuite']['id'],
            pointData['testCaseReference']['id'],
            pointData['configuration']['id']))
    return points

  def __listConfigs(self):
    print(f'Listing test configs')
    uri = f'{self._baseUri}/testplan/configurations'
    jsons = self._get(uri, True)
    self.__testConfigs = []
    for json in jsons:
      for configData in json['value']:
        self.__testConfigs.append(
          TestConfig(
            configData['id'],
            configData['name'],
            configData['description']))

  def Print(self):
    for testSuite in self.__testSuites:
      print(testSuite)
    for testCase in self.__testCases:
      print(testCase)
    for testConfig in self.__testConfigs:
      print(testConfig)
    for testPoint in self.__testPoints:
      print(testPoint)
    print(self.__testTags)

def main():
  config = Config('azuretest.json')
  testPlan = TestPlan(config.projectUri, config.token, config.testPlanId)
  testPlan.Print()

if __name__ == '__main__':
  main()
