if __name__ == "__main__":
    from icalendar import Calendar, Event, Alarm
    from datetime import timedelta
    from modules import load
    from modules.nebutil.log import LOGGER
    from modules.nebutil.time import DateUtil
    from modules.events import EventType
    from argparse import ArgumentParser
    
    PARSER = ArgumentParser(prog="main.py", description="This program generates an ICS calendar file with the Pokémon Go events data scrapped from the https://www.leekduck.com website.")
    PARSER.add_argument("-d", "--downloadImg", help="Download images", action="store_true")
    PARSER.add_argument("-u", "--update", help="Force events to update", action="store_true")
    ARGS = PARSER.parse_args()
    
    downloadImg:bool = ARGS.downloadImg
    
    CAL = Calendar()
    CALENDAR_FILE = 'cal.ics'
    EVENTS = load(downloadImg)
    E = EVENTS.ofTypes(EventType.all())

    LOGGER.info(f'Generating calendar file for {len(E)} events...')
    for event in E:
        icsEvent = Event()
        icsEvent.add('summary', event.name)
        icsEvent.add('dtstart', DateUtil.fromStr(event.startDate,'%Y-%m-%d %H:%M:%S').date)
        icsEvent.add('dtend', DateUtil.fromStr(event.endDate,'%Y-%m-%d %H:%M:%S').date)
        desc = event.contentStr()
        icsEvent.add('description',desc)
        alarms = [Alarm() for _ in range(3)]
        alarms[0].add('trigger',timedelta(minutes=-30))
        alarms[1].add('trigger',timedelta(hours=-1))
        alarms[2].add('trigger',timedelta(hours=-3))
        for alarm in alarms:
            alarm.add('action','display')
            icsEvent.add_component(alarm)
        CAL.add_component(icsEvent)

    LOGGER.info(f'Writing calendar data in {CALENDAR_FILE}...')
    with open(CALENDAR_FILE, 'w') as calendarFile:
        calendarFile.writelines(CAL.to_ical().decode("utf-8"))
    LOGGER.info('Done!')
