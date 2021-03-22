
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
        self.uri = config['connection']['uri']
        self.token = config['connection']['token']
        self.project = config['connection']['project']
        self.testPlanId = config['connection']['testPlanId']
      except ValueError:
        print(f'Failed to load json from {fname}')
        return

def main():
  config = Config('azuretest.json')

if __name__ == '__main__':
  main()
