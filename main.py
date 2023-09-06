import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--test', type=str, default="hello")

    args = dict(vars(parser.parse_args()))

    print(args['test'])
