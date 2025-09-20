from pathlib import Path
from typing import List
from auryl import parser
import argparse
import sys

def main():
    files = [Path(file) for file in sys.argv[1:]]
    parser.parse(files)
