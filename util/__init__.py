import subprocess
def flatten(lst):
  return sum(([x] if not isinstance(x, list) else flatten(x)
         for x in lst), [])

def sh(cmd):
  try: 
    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
  except Exception, e:
    output = str(e.output)
  return output


debug = False

from git.util import RemoteProgress
class DisProgress(RemoteProgress):
  if debug:
    def line_dropped(self, line):
      print('{0}'.format(line))
    def update(self, op_code, cur_count, max_count=None, message=''):
      print('{0} {1}/{2} {3}'.format(op_code, cur_count, max_count, message))

