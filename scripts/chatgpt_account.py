"""Manage this installation's local ChatGPT subscription authorization."""
import argparse
import json
import os
from chatgpt_auth import ChatGPTAuth


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['status', 'login', 'models'])
    parser.add_argument('--account')
    parser.add_argument('--enable-plan', action='store_true')
    args = parser.parse_args()
    auth = ChatGPTAuth()
    if args.command == 'login':
        result = auth.sign_in(args.account, enable_plan=args.enable_plan)
    elif args.command == 'models':
        result = auth.models(args.account)
    else:
        result = auth.status(args.account)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
