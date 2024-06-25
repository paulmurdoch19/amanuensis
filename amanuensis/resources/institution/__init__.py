from amanuensis.resources.userdatamodel import (
    get_institution,
	get_all_institutions,
    update_institution,
    add_institution,
)
import requests, json
def api_request(name):
    """
    Makes a call to the Consolidated Screening List api of developer.trade.gov. Information returned in the dictionary
    can be accessed by info_dict["results"], which is a list of dictionaries containing information about the legality
    of interacting with the returned companies.
    """
    try:
        url = f"https://data.trade.gov/consolidated_screening_list/v1/search?name={name}"
        hdr ={
        # Request headers
        'Cache-Control': 'no-cache',
        'subscription-key': 'a7c2cd5a313d430c9df8bc7918f2e14b',
        }

        response = requests.get(url, headers=hdr)

        code = response.status_code
        r = response.text
        info_dict = {}
        if(code == 200):
            info_dict = json.loads(r)
        else:
            print("Request unsuccessful: error {code}")
        return info_dict
    except Exception as e:
        print(e)

