import getopt
import sys
from lensesio.lenses import main as lenses
import json
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

credentials = ''
lensesUrl = ''
sqlCommand = ''

try:
   options, args = getopt.getopt(sys.argv[1:], "c:u:s:",["credentials=", "url=", "sql="])
except getopt.GetoptError:
    sys.exit( 'Lenses python command not correctly called. should be: lenses.py -c <name of env variable hold token with format: service_owner:service-token> -u <lensesUrl> -s <Sql command>')
# Get Options
for name, value in options:
  if name in ('-c', '--credentials'):
    credentials = os.getenv(value)
  if name in ('-u', '--url'):
    lensesUrl = value
  if name in ('-s', '--sql'):
    sqlCommand = value

try:
  connection=lenses(auth_type="service", url=lensesUrl,service_account=credentials)
except: 
  raise Exception("Error connecting to Lenses on %s" %lensesUrl)
  # sys.exit("Error connecting to Lenses on %s" %lensesUrl)

query = (sqlCommand)
try:
  result = connection.ExecSQL(query)
except Exception as e:
  raise Exception("Error running sql query. error was %s" %e)
#   sys.exit("Error %s running SQL %s on Lenses %s" %(e,query,lensesUrl))
  

try:
  data = result["data"]
except Exception as e:
  raise Exception("Error %s getting results from SQL %s on Lenses %s" %(e,query,lensesUrl))
print(json.dumps(data))

