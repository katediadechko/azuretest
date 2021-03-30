
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

class TestPlanClient(RestClient):
  def __init__(self, projectUri, accessToken, testPlanId):
    RestClient.__init__(self, projectUri, accessToken)
    self.__testPlanId = testPlanId

  def GetWorkitem(self, id):
    uri = f'{self._baseUri}/wit/workitems/?ids={id}'
    widata = self._get(uri, False)[0]['value'][0]
    wi = Workitem(
      widata['id'],
      widata['rev'],
      widata['fields']['System.Description'] if 'System.Description' in widata['fields'] else '')
    return wi

  def ListSuites(self):
    uri = f'{self._baseUri}/testplan/Plans/{self.__testPlanId}/Suites'
    jsons = self._get(uri, True)
    suites = []
    for json in jsons:
      for suiteData in json['value']:
        workitem = self.GetWorkitem(suiteData['id'])
        suites.append(
          TestSuite(
            suiteData['id'],
            suiteData['name'],
            workitem.desc,
            TestSuiteType[suiteData['suiteType']],
            suiteData['parentSuite']['id'] if 'parentSuite' in suiteData else None))
    return suites

  def ListCases(self, suiteId):
    uri = f'{self._baseUri}/testplan/Plans/{self.__testPlanId}/Suites/{suiteId}/TestCase'
    jsons = self._get(uri, True)
    cases = []
    for json in jsons:
      for caseData in json['value']:
        workitem = self.GetWorkitem(caseData['workItem']['id'])
        cases.append(
          TestCase(
            caseData['workItem']['id'],
            caseData['workItem']['name'],
            workitem.desc))
    return cases

  def ListPoints(self, suiteId):
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

  def ListConfigs(self):
    uri = f'{self._baseUri}/testplan/configurations'
    jsons = self._get(uri, True)
    configs = []
    for json in jsons:
      for configData in json['value']:
        configs.append(
          TestConfig(
            configData['id'],
            configData['name'],
            configData['description']))
    return configs

def main():
  config = Config('azuretest.json')
  testPlanClient = TestPlanClient(config.projectUri, config.token, config.testPlanId)
  testSuites = testPlanClient.ListSuites()
  for testSuite in testSuites:
    print(testSuite)
    testCases = testPlanClient.ListCases(testSuite.id)
    for testCase in testCases:
      print(f'\t{testCase}')
    print()
    testPoints = testPlanClient.ListPoints(testSuite.id)
    for testPoint in testPoints:
      print(f'\t{testPoint}')
    print()
  print()
  testConfigs = testPlanClient.ListConfigs()
  for testConfig in testConfigs:
    print(testConfig)

if __name__ == '__main__':
  main()
