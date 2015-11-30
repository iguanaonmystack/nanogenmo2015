import subprocess
import os
import sys


while True:
    with open('output/novel.md', 'w') as out:
        try:
            subprocess.run(['python3', 'novel.py', '-x6', '-y6', '-p6'], stdout=out, timeout=30)
        except subprocess.TimeoutExpired:
            print('timeout')
    wc = subprocess.run(['wc', '-w', 'output/novel.md'], stdout=subprocess.PIPE, universal_newlines=True)
    words = int(wc.stdout.strip().split(' ')[0])
    print(words)
    if 50000 < words < 100000:
        break
