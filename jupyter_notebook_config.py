# Configuration file for notebook.
c = get_config()  # type: ignore #noqa
c.ServerApp.browser = '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --incognito %s'
