import sys
import random
import argparse
import logging

import novel

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='NaNoGenMo 2015 novel generator.')
    parser.add_argument('-x', dest='xsize', type=int, default=32,
        help='X (West-East) dimension of world')
    parser.add_argument('-y', dest='ysize', type=int, default=32,
        help='Y (North-South) dimension of world')
    parser.add_argument('-r', '--random-seed', dest='seed', type=int,
        default=None, help='Random seed')
    parser.add_argument('-p', '--people', dest='people', type=int, default=12,
        help='Number of people in world')
    parser.add_argument('-v', dest='verbose', action='store_true',
        help='Verbose (debugging) mode')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    if not args.seed:
        args.seed = random.randint(0, sys.maxsize)
    random.seed(args.seed)
    print('World size: %dx%d' % (args.xsize, args.ysize))
    print('Random seed: %d' % args.seed)
    print()
    novel.novel(args.xsize, args.ysize, args.people)
    print()
    print('Random seed: %d' % args.seed)

