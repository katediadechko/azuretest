
from enum import Enum
from collections import namedtuple

Workitem = namedtuple('Workitem', 'id rev desc')

TestSuiteType = Enum('TestSuiteType', 'staticTestSuite requirementTestSuite dynamicTestSuite')
TestSuite = namedtuple('TestSuite', 'id name desc type parentId')
TestCase = namedtuple('TestCase', 'id name desc')
TestConfig = namedtuple('TestConfig', 'id name desc')
TestPoint = namedtuple('TestPoint', 'id testSuiteId testCaseId testConfigId')
