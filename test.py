from datetime import datetime
import re

# print(re.findall('[0-9]+', str(datetime.now())))
print("".join(re.findall('[0-9]+', str(datetime.now()))))