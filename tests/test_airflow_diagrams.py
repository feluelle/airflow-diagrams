import subprocess
import unittest


class TestAirflowDiagrams(unittest.TestCase):
    def test_run_example_dag(self):
        subprocess.call(['python', 'examples/dags/example_dag.py'])


if __name__ == '__main__':
    unittest.main()
