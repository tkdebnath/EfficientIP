import hashlib
import json
import time
import requests
from urllib.parse import urljoin, urlencode
from urllib3 import disable_warnings

# import from config
from config import Token_ID, Token_Secret
from config import Hostname, DNS_Name

disable_warnings()


def final_url_generate(base_url, params):
    encoded_params = urlencode(params, doseq=True)
    final_url = urljoin(base_url, "?" + encoded_params)
    return final_url

def headers_url(method, base_url, params):
    url = final_url_generate(base_url,params)

    ts = str(int(time.time()))
    string = f"{Token_Secret}\n{ts}\n{method}\n{url}"
    string_encode = string.encode('utf-8')
    final_sign = hashlib.sha3_256(string=string_encode).hexdigest()
    return {
        'url': url,
        'headers': {
            "Authorization": f"SDS {Token_ID}:{final_sign}",
            "X-SDS-TS": ts,
            "Accept": "application/json"
        }
    }


def dhcp_lease(address):
    base_url = f"{Hostname}/rest/dhcp_range_lease_list"
    METHOD = "GET"
    querystring = {"WHERE":f"dhcplease_addr='{address}'"}

    get_headers_url = headers_url(method=METHOD, 
                                  base_url=base_url, 
                                  params=querystring)

    response = requests.request(METHOD, get_headers_url['url'], headers=get_headers_url['headers'], verify=False)
    response.raise_for_status()

    if response.status_code == 200:
        lease_info = json.loads(response.text)
        if len(lease_info) > 0:
            result = {}
            result['address'] = lease_info[0]['dhcplease_addr']

            if lease_info[0].get('dhcplease_clientname', '') != '':
                result['client_hostname'] = lease_info[0]['dhcplease_clientname']
            
            if lease_info[0].get('dhcplease_mac_addr', '') != '':
                result['hardware'] = lease_info[0]['dhcplease_mac_addr']
            return result
        return None
    else:
        return None
    
def dns_rr_list(rr_name=None, addr_ipv4=None):
    base_url = f"{Hostname}/rest/dns_rr_list"
    METHOD = "GET"
    
    if addr_ipv4 and not rr_name:
        querystring = {"WHERE": f"value1='{addr_ipv4}' or value2='{addr_ipv4}' or value3='{addr_ipv4}' or value4='{addr_ipv4}' or value5='{addr_ipv4}' or value6='{addr_ipv4}' or value7='{addr_ipv4}'"}
        
    if not addr_ipv4 and rr_name:
        if "." in rr_name:
            querystring = {"WHERE": f"rr_full_name='{rr_name}'"}
        else:
            querystring = {"WHERE": f"rr_glue='{rr_name}'"}
    
    if addr_ipv4 and rr_name:
        if "." in rr_name:
            querystring = {"WHERE": f"rr_full_name='{rr_name}' and value1='{addr_ipv4}'"}
        else:
            querystring = {"WHERE": f"rr_glue='{rr_name}' and value1='{addr_ipv4}'"}
        
    if not addr_ipv4 and not rr_name:
        return "Enter valid DNS name or IP"

    get_headers_url = headers_url(method=METHOD, 
                                  base_url=base_url, 
                                  params=querystring)

    response = requests.request(METHOD, get_headers_url['url'], headers=get_headers_url['headers'], verify=False)
    response.raise_for_status()

    if response.status_code == 200:
        dns_rr_info = json.loads(response.text)
        if len(dns_rr_info) > 0:
            result = {
                "rr_type": dns_rr_info[0]['rr_type'],
                "addr_ipv4": dns_rr_info[0]['value1'],
                "record": dns_rr_info[0]['rr_full_name_utf']
            }

            return result
        return None
    else:
        return None
    

# New DNS A record
def dns_rr_add(rr_name, addr_ipv4, rr_type="A"):
    #  Mandatory Input Parameters
    # • Addition: (rr_name && rr_type && value1 && (dns_id || dns_name || hostaddr))
    # • Editing: (rr_id || (rr_name && rr_type && value1 && (dns_id || dns_name || hostaddr)))
    
    base_url = f"{Hostname}/rest/dns_rr_add"
    METHOD = "POST"
    params = {
        "rr_name": rr_name,
        "rr_type": rr_type,
        "value1": addr_ipv4,
        "dns_name": DNS_Name
        }

    get_headers_url = headers_url(method=METHOD, 
                                  base_url=base_url, 
                                  params=params)

    response = requests.request(METHOD, get_headers_url['url'], headers=get_headers_url['headers'], verify=False)
    response.raise_for_status()
    if response.status_code == 201:
        dns_rr_info = json.loads(response.text)
        if len(dns_rr_info) == 1:
            result = {
                "ret_oid": dns_rr_info[0]['ret_oid']
            }

            return result
        return None
    else:
        return None
    

if __name__=='__main__':
    pass
    

