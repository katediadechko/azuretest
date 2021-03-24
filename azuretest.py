
from atconfig import *
from attypes import *

import json
import base64
import requests

class RestClientError(Exception):
  pass

class RestClient:
  _connectTimeout = 5
  _readTimeout = 120

  def __init__(self, baseUri, accessToken):
    baseUri.rstrip('/')
    self._baseUri = baseUri + '/_apis'
    self.__session = requests.Session()
    accessToken += ':'
    tokenBase64 = b'Basic ' + base64.b64encode(accessToken.encode("utf8"))
    self.__session.headers.update({'Authorization': tokenBase64})

  def _get(self, uri):
    res = []
    contToken = ''
    while True:
      contUri = uri + f'?$top=200&continuationtoken={contToken}'
      response = self.__session.get(contUri, timeout = (self._connectTimeout, self._readTimeout))
      response.raise_for_status()

      try:
        json = response.json()
        res.append(json)
      except ValueError:
        raise RestClientError(f'Failed to convert response to JSON: {response.text}')

      if 'x-ms-continuationtoken' in response.headers:
        contToken = response.headers['x-ms-continuationtoken']
      else:
        break
    return res

class TestPlanClient(RestClient):
  def __init__(self, projectUri, accessToken, testPlanId):
    RestClient.__init__(self, projectUri, accessToken)
    self.__testPlanId = testPlanId

  def GetSuites(self):
    uri = f'{self._baseUri}/testplan/Plans/{self.__testPlanId}/Suites'
    jsons = self._get(uri)
    suites = []
    for json in jsons:
      for suiteData in json['value']:
        parentSuiteId = suiteData['parentSuite']['id'] if 'parentSuite' in suiteData else None
        suites.append(TestSuite(suiteData['id'], suiteData['name'], TestSuiteType.Parse(suiteData['suiteType']), parentSuiteId))
    return suites

def main():
  config = Config('azuretest.json')
  testPlanClient = TestPlanClient(config.projectUri, config.token, config.testPlanId)
  testSuites = testPlanClient.GetSuites()
  for testSuite in testSuites:
    testSuite.Print()

if __name__ == '__main__':
  main()
