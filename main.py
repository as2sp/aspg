import random
import string
import pyperclip
import configparser
import logging


def process_config_file():
    with open('config.ini', 'r') as file:
        for line in file:
            if line.startswith('special_symbols'):
                special_symbols_str = line.split('=')[1].strip()
                special_symbols_list = list(special_symbols_str)
            if line.startswith('min_distance'):
                min_char_distance = int(line.split('=')[1].strip())

    config = configparser.ConfigParser()
    config.read('config.ini')

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

    enable_logging = config.getboolean('log', 'enable')
    if enable_logging:
        log_filename = config.get('log', 'filename')

    if min_char_distance < 0 or min_char_distance > 4:
        print("min_char_distance must be between 0 and 4 in config.ini. Program terminated.")
        if enable_logging:
            logging.basicConfig(filename=log_filename, level=logging.INFO, format='[%(asctime)s] %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
            logging.info("min_char_distance more than 4 in config.ini. Program terminated.")
        raise SystemExit

    return special_symbols_list, min_char_distance, characters, enable_logging, config


def write_to_log(password_length, clipboard_result, password, config):
    enable_logging = config.getboolean('log', 'enable')
    if enable_logging:
        log_filename = config.get('log', 'filename')
        print(f"Writing this event to log {log_filename}.")
        show_pass = config.getboolean('log', 'show_pass')

        logging.basicConfig(filename=log_filename, level=logging.INFO, format='[%(asctime)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

        if show_pass:
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

                print("Your password:", password)
                print()

                copy_to_clipboard = input("Do you want to copy the result to the clipboard? (y/n): ")

                if copy_to_clipboard.lower() == "y":
                    pyperclip.copy(str(password))
                    clipboard_result = "and it has been copied to the clipboard"
                else:
                    clipboard_result = "and it has not been copied to the clipboard"

                write_to_log(password_length, clipboard_result, password, config)

                input("Press Enter to exit.")
                break

        except ValueError:
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


if __name__ == "__main__":
    main()