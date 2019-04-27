import sys

if __name__ == '__main__':
    if len(sys.argv) > 0:
        path = sys.argv[1]
        print('Called from', path)