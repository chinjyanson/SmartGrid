import time
import random
import string

file_path = 'C:/Users/samue/Desktop/SmartGrid/react-front-end/src/assets/TEST_FILE.txt'

while True:
    text_to_write = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    with open(file_path, 'w') as file:
        file.write(text_to_write)
    time.sleep(5)