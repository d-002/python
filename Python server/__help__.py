def func_exit():
    return """Close the window and disconnect from the server."""

def func_ip():
    return """Print client IP, client port, server IP, server port."""

def func_cd():
    return """Changes current directory to specified one.
Syntax: cd {folder name}"""

def func_set_admin():
    return """Request the server for being administrator.
After a set amount of time, the server will automatically refuse the request."""

def func_stop_server():
    return """Stops the server if the client has previously been added to the administrators."""

def func_view_url():
    return """Prints the content of the html corresponding to the specified internet address.
Syntax: view_url {http(s)://url}"""

def func_download_url():
    return """Downloads the content of the html corresponding to the specified internet address.
(request the html, then ask where to copy the content into a file)
Syntax: view_url {http(s)://url}"""

def func_send_file():
    return """Send a file to the server, which will then be asked where to put it.
Syntax: send_file {filename}"""

def func_msg():
    return """Send a message to the server
Syntax: msg {message}"""

general = """You can put quotes " around addresses and file paths.
Please only request valid URLs and files paths."""

def get_globals():
    dict_ = {'__general__': general}
    for function in [globals()[g] for g in globals() if g.startswith('func_')]:
        dict_[function.__name__.split('func_')[1]] = function()
    return dict_
