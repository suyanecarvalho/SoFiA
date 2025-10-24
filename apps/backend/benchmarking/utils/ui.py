import colorama

colorama.init(autoreset=True)

def print_success(message):
    print(colorama.Fore.GREEN + "[SUCCESS] " + message)

def print_failure(message):
    print(colorama.Fore.RED + "[FAILURE] " + message)

def print_info(message):
    print(colorama.Fore.CYAN + "[INFO] " + message)

def print_warning(message):
    print(colorama.Fore.YELLOW + "[WARN] " + message)