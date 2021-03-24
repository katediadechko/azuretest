
import json
import base64
import requests

class Config:
  def __init__(self, fname):
    try:
      f = open(fname, 'r')
    except OSError:
      print(f'Failed to open file: {fname}')
      return
    with f:
      try:
        config = json.load(f)
        self.projectUri = config['connection']['projectUri']
        projectUriChunks = self.projectUri.rstrip('/').split('/')
        self.collection = projectUriChunks[-2]
        self.project = projectUriChunks[-1]
        self.baseUri = '/'.join(projectUriChunks[:-2]) + '/'
        self.token = config['connection']['token']
        self.testPlanId = config['connection']['testPlanId']
      except ValueError:
        print(f'Failed to load json from: {fname}')
        return

class RestClientError(Exception):
  pass

class RestClient:
  def __init__(self, uri, token):
    uri.rstrip('/')
    self.uri = uri + '/_apis'
    self.session = requests.Session()
    self.connectTimeout = 5
    self.readTimeout = 120
    token += ':'
    tokenBase64 = b'Basic ' + base64.b64encode(token.encode("utf8"))
    self.session.headers.update({'Authorization': tokenBase64})

  def __get(self, uri):
    res = []
    contToken = ''
    while True:
      contUri = uri + f'?$top=200&continuationtoken={contToken}'
      response = self.session.get(contUri, timeout = (self.connectTimeout, self.readTimeout))
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

  def GetTestPlanData(self, testPlanId):
    uri = f'{self.uri}/testplan/Plans/{testPlanId}/Suites'
    return self.__get(uri)

def main():
  config = Config('azuretest.json')
  client = RestClient(config.projectUri, config.token)
  print(client.GetTestPlanData(config.testPlanId))

if __name__ == '__main__':
  main()
