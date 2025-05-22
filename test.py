import os
stations = ['jp','my','sg','kr','au','nz','eg','za','ae','qa','ru']
for station in stations:
    cmd =f'python serper_company_search.py  --general-search --custom-query "project partner of digital signature"  --gl {station} '
    os.system(cmd)
