
import json

class Config:
  def __init__(self, fname):
    try:
      f = open(fname, 'r')
    except OSError:
      print(f'Failed to open file {fname}')
      return
    with f:
      try:
        config = json.load(f)
        projectUriChunks = config['connection']['projectUri'].rstrip('/').split('/')
        self.collection = projectUriChunks[-2]
        self.project = projectUriChunks[-1]
        self.baseUri = '/'.join(projectUriChunks[:-2]) + '/'
        self.token = config['connection']['token']
        self.testPlanId = config['connection']['testPlanId']
      except ValueError:
        print(f'Failed to load json from {fname}')
        return

def main():
  config = Config('azuretest.json')

if __name__ == '__main__':
  main()
