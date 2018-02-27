import argparse
import requests
import json

baseurl = "http://localhost:5000/api"

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=['create', 'list', 'update'],
                        help="create/list/update")
    parser.add_argument("domain", type=str, nargs='?',
                        help="Domain name")
    parser.add_argument("password", type=str,
                        help="Domain password")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")

    args = parser.parse_args()

    config = {}
    config['domain'] = args.domain
    config['password'] = args.password

    if args.action == "create":
        # send request
        url = baseurl + "/domain/create"
        r = requests.post(url, json=config)

        # domain password sent as response
        print(r.text)

    elif args.action == "list":
        # send request
        url = baseurl + "/domain/list"
        r = requests.post(url, json=config)
        if r:
            print(json.dumps(r.json(), indent=4, sort_keys=True))
        else:
            print(r.text)

    elif args.action == "update":
        # send request
        url = baseurl + "/domain/update"
        r = requests.post(url, json=config)
        print(r.text)
