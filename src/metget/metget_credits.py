#!/usr/bin/env python3
###################################################################################################
# MIT License
#
# Copyright (c) 2023 The Water Institute
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author: Zach Cobell
# Contact: zcobell@thewaterinstitute.org
# Organization: The Water Institute
#
###################################################################################################
import argparse


def metget_credits(args: argparse.Namespace) -> None:
    """
    This method is used to get the number of credits available

    Args:
        args: The arguments passed to the command line
    """
    import requests
    import prettytable
    from .metget_environment import get_metget_environment_variables

    env = get_metget_environment_variables(args)

    url = env["endpoint"] + "/credits"
    headers = {"x-api-key": env["apikey"]}
    response = requests.get(url, headers=headers)

    if args.format == "json":
        print(response.json())
    elif args.format == "pretty":
        table = prettytable.PrettyTable(
            ["Credit Limit", "Credits Used", "Credit Balance"]
        )
        credit_limit = response.json()["body"]["credit_limit"]
        if credit_limit == 0:
            credit_limit = "Unlimited"
        credit_balance = response.json()["body"]["credit_balance"]
        if credit_balance == 0:
            credit_balance = "Unlimited"
        table.add_row(
            [
                credit_limit,
                response.json()["body"]["credits_used"],
                credit_balance,
            ]
        )
        print("Credit status for apikey: " + env["apikey"])
        print(table)
    else:
        raise RuntimeError("Invalid format: " + args.format)
