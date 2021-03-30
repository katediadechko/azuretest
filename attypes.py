
from enum import Enum
from collections import namedtuple

TestSuiteType = Enum('TestSuiteType', 'staticTestSuite requirementTestSuite dynamicTestSuite')
TestSuite = namedtuple('TestSuite', 'id name type parentId')
