# cap_sender

Retrieve today's payload for all sources defined in `sources.py`:
```bash
python main.py --config config.ini
```

Retrieve only the designated sources from `sources.py`:
```bash
python main.py --config config.ini --sources cap_applications cap_transcripts
```

## configuration
All authentication and host configurations should be set in an .ini file or as environment variables.

For each payload type, the payload should be defined in `sources.py`. Each payload should be a dictionary with the following elements:
```python
SOURCES = [
  {
    'name': 'machine_friendly_name',  # referenced with the -s arg
    'pattern': '{}_filename.zip',  # the note wildcard format braces
    'dttm_fmt': '%m%d%Y',  # used to fill today's date in the pattern above
    'source': '12312-12125-1353135-13131'  # guid of destination source format
  }
]
```
## ZipProcessor Class
If a new source requires any transformations before being sent to the destination, define a new `ZipProcessor` class and implement the `.transform` method to fit.
