from metget.metget_client import metget_client_cli


def test_cli():
    """
    Test fires the CLI. This doesn't do much except check that argparse can fire up correctly

    Returns:
        None
    """
    metget_client_cli()
