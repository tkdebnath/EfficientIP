# Author: Tarani Debnath

from helper import dns_rr_list, dns_rr_add

# Pandas to read CSV and Excel files
import pandas as pd

if __name__=='__main__':
    # Load src file containing data
    # Required columns: Hostname, IP
    file_name = ".xlsx"
    
    df = pd.read_excel(file_name, usecols=['Hostname', 'IP'])
    
    # Reading all rows
    for i, row in df.iterrows():
        print(f"Checking for DNS record for {row['Hostname']}, {row['IP']}")
        
        check = dns_rr_list(rr_name=row['Hostname'], addr_ipv4=row['IP'])
        if not check:
            rr_create = dns_rr_add(rr_name=row['Hostname'], addr_ipv4=row['IP'])
            if rr_create:
                print(f"DNS record created for {row['Hostname']}, {row['IP']}")
            else:
                print(f"Operation failed for {row['Hostname']}, {row['IP']}")
        else:
            print(f"DNS record already exist for {row['Hostname']}, {row['IP']}")