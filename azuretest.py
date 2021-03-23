
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
        self.projectUri = config['connection']['projectUri']
        self.token = config['connection']['token']
        self.testPlanId = config['connection']['testPlanId']
        self.collection = self.projectUri.split('/')[-2]
        self.project = self.projectUri.split('/')[-1]
      except ValueError:
        print(f'Failed to load json from {fname}')
        return

def main():
  config = Config('azuretest.json')
  print(config.collection)
  print(config.project)

if __name__ == '__main__':
  main()
