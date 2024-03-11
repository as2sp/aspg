import random
import string
import pyperclip
import configparser
import logging


def process_config_file():
    # Processing special chars list in config.ini
    with open('config.ini', 'r') as file:

        for line in file:

            if line.startswith('special_symbols'):
                special_symbols_str = line.split('=')[1].strip()
                special_symbols_list = list(special_symbols_str)
            if line.startswith('min_distance'):
                min_char_distance = int(line.split('=')[1].strip())

    config = configparser.ConfigParser()
    config.read('config.ini')

    # Processing common chars list in config.ini
    symbols = config.get('chars', 'symbols')
    if symbols == 'letters':
        characters = string.ascii_lowercase
    elif symbols == 'LETTERS':
        characters = string.ascii_uppercase
    elif symbols == 'digits':
        characters = string.digits
    elif ',' in symbols:
        symbol_list = symbols.split(',')
        result = ''

        for symbol in symbol_list:

            if symbol == 'letters':
                result += string.ascii_lowercase
            elif symbol == 'LETTERS':
                result += string.ascii_uppercase
            elif symbol == 'digits':
                result += string.digits
            else:
                result += symbol
        characters = result

    else:
        characters = symbols

    # Check that logging is enabled in config.ini
    enable_logging = config.getboolean('log', 'enable')
    if enable_logging:
        log_filename = config.get('log', 'filename')

    # Check that the minimum number of common chars between special chars is between 0 and 4
    if min_char_distance < 0 or min_char_distance > 4:
        print("min_char_distance must be between 0 and 4 in config.ini. Program terminated.")

        if enable_logging:
            logging.basicConfig(filename=log_filename, level=logging.INFO, format='[%(asctime)s] %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
            logging.info("min_char_distance less than 0 or more than 4 in config.ini. Program terminated.")
        raise SystemExit

    return special_symbols_list, min_char_distance, characters, enable_logging, config


def write_to_log(password_length, clipboard_result, password, config):
    # Start logging if enabled in config.ini
    enable_logging = config.getboolean('log', 'enable')

    if enable_logging:
        log_filename = config.get('log', 'filename')
        print()
        print(f"Writing this event to log {log_filename}.")
        show_pass_in_log = config.getboolean('security', 'show_pass_in_log')

        logging.basicConfig(filename=log_filename, level=logging.INFO, format='[%(asctime)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

        # show_password setting logging here
        if show_pass_in_log:
            logging.info(
                f"Password length is {password_length} chars, {clipboard_result}. Generated password: {password}")
        else:
            logging.info(f"Password length is {password_length} chars, {clipboard_result}. "
                         "The password has not been logged.")


def main():
    special_symbols_list, min_char_distance, characters, enable_logging, config = process_config_file()

    while True:
        try:
            password_length = int(input("Enter the number (not less than 5) of password characters: "))

            if password_length > 4:
                special_char_count = password_length // (random.randint(8, 10)) + 1
                min_distance = min_char_distance + 1
                special_char_positions = []

                while len(special_char_positions) < special_char_count:
                    position = random.randint(0, password_length - 1)

                    if all(abs(position - sp) >= min_distance for sp in special_char_positions):
                        special_char_positions.append(position)

                password = ""

                for i in range(password_length):

                    if i in special_char_positions:
                        password += random.choice(special_symbols_list)
                    else:
                        password += random.choice(characters)

                # Check show_password setting
                if config.getboolean('security', 'show_password'):
                    print()
                    print("Your password:", password)
                    print()
                    copy_to_clipboard = input("Do you want to copy the result to the clipboard? (y/n): ")

                    # Process copy-to-buffer action
                    if copy_to_clipboard.lower() == "y":
                        pyperclip.copy(str(password))
                        clipboard_result = "and it has been copied to the clipboard"
                    else:
                        clipboard_result = "and it has not been copied to the clipboard"

                # If show_password setting is false run this block
                else:
                    hidden_password = "*" * password_length
                    print()
                    print("Your password:", hidden_password)
                    pyperclip.copy(str(password))
                    print()
                    print("The password has been automatically copied to the clipboard because the security setting "
                          "in the config.ini file hides the display of the password.")
                    clipboard_result = "and it has been copied to the clipboard"

                write_to_log(password_length, clipboard_result, password, config)
                print()
                input("Press Enter to exit.")
                break

        except ValueError:
            print()
            print('Invalid format, non-numeric characters entered.')
            print()
        except KeyboardInterrupt:

            if enable_logging:
                log_filename = config.get('log', 'filename')
                logging.getLogger().handlers = []
                logging.basicConfig(filename=log_filename, level=logging.INFO, format='[%(asctime)s] %(message)s',
                                    datefmt='%Y-%m-%d %H:%M:%S')
                logging.info(f"The program terminated unexpectedly.")
            raise


# Main app starts here
if __name__ == "__main__":
    main()