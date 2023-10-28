from argparse import ArgumentParser
PARSER = ArgumentParser(description="This program generates an ICS calendar file with the Pokémon Go events data scrapped from the https://www.leekduck.com website. Note that the usage of the website's data is not for commercial purposes and the usage of this program must not be either.")
PARSER.add_argument("-d", "--downloadImg", help="Downloads images", action="store_true")
PARSER.add_argument("-u", "--update", help="Forces update", action="store_true")
PARSER.add_argument("-o", "--output", help="Output file name", default="cal.ics",type=str)
PARSER.add_argument("-v", "--verbose", help="Verbose mode", action="store_true")
PARSER.add_argument("-q", "--quiet", help="Quiet mode", action="store_true")
ARGS = PARSER.parse_args()
print(ARGS)