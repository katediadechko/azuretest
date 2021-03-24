
class TestSuiteType():
  Static = 0
  Requirement = 1
  Query = 2

  @staticmethod
  def Parse(str):
    if str == 'staticTestSuite':
      return TestSuiteType.Static
    elif str == 'requirementTestSuite':
      return TestSuiteType.Requirement
    elif str == 'dynamicTestSuite':
      return TestSuiteType.Query
    else:
      raise ValueError(f'Failed to convert test suite type: {str}')

class TestSuite():
  def __init__(self, id, name, type, parentId):
    self.__id = id
    self.__name = name
    self.__type = type
    self.__parentId = parentId

  def Print(self):
    print(f'{self.__id} \'{self.__name}\' {self.__type} {self.__parentId}')
