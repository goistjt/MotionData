import unittest
import tests.kinematics_test as kt


def suite():
    suite_to_run = unittest.TestSuite()
    suite_to_run.addTests(unittest.makeSuite(kt.TestKinematics))
    return suite_to_run


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
