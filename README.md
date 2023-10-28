# pokemongo-calendar

## Description
This project aims to create a ICS calendar file of Pokémon events registered on the [LeekDuck](https://leekduck.com/) website for a personal use.

## Usage
### Requirements
- Python 3.6+
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
- [html5lib](https://pypi.org/project/html5lib/)
- [icalendar](https://pypi.org/project/icalendar/)

### Execution
```bash
python3 main.py [-h] [-o OUTPUT] [-d] [-v] [-q] [-u]
```

### Options
| Option | Description |
| --- | --- |
| `-h, --help` | Show the help message and exit |
| `-o OUTPUT, --output OUTPUT` | Output file path |
| `-d, --downloadImg` | Download images |
| `-u, --update` | Force update of the events |
| `-v, --verbose` | Enable verbose mode |
| `-q, --quiet` | Enable quiet mode |