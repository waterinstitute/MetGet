#!/usr/bin/env python3
################################################################################
# MetGet Client
#
# This file is part of the MetGet distribution (https://github.com/waterinstitute/metget).
# Copyright (c) 2023, The Water Institute
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Author: Zach Cobell, zcobell@thewaterinstitute.org
#
################################################################################
import argparse


def metget_credits(args: argparse.Namespace) -> None:
    """
    This method is used to get the number of credits available

    Args:
        args: The arguments passed to the command line
    """
    import requests
    import prettytable
    from metgetclient.metget_environment import get_metget_environment_variables

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
