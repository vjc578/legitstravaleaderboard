from html.parser import HTMLParser
from collections import namedtuple
import sys
import subprocess
import json
import time
from enum import Enum

CollectedData = namedtuple('Data', 'rankings, segment_count')

class SegmentHTMLParser(HTMLParser):
    class State(Enum):
        INITIAL = 1
        FOUND_TRACK_CLICK = 2
        FOUND_PERSON = 3
        SET_PERSON = 4
        FOUND_TIME = 5

    def __init__(self, config):
        self.state = self.State.INITIAL
        self.person = None
        self.config = config
        self.count = 0
        super().__init__()

    def handle_person(self, person, seconds):
        print("hi")

    def handle_starttag(self, tag, attrs):
      if self.state is self.State.SET_PERSON:
        if tag == 'td':
            for attr in attrs:
                if (attr[0] == "class" and attr[1] == "last-child"):
                    self.state = self.State.FOUND_TIME
        return

      if self.state is self.State.FOUND_TRACK_CLICK:
        if tag == 'a':
            self.state = self.State.FOUND_PERSON
        return

      if self.state is self.State.INITIAL and tag == 'td':
        for attr in attrs:
            if attr[0] == "class" and attr[1] == "athlete track-click":
                self.state = self.State.FOUND_TRACK_CLICK

    def handle_data(self, data):
        if self.state is self.State.FOUND_TIME:
            seconds = 0
            parts = data.split(":")
            if len(parts) is 1:
                # Format is number followed by an s (e.g. 49s) for seconds
                seconds = int(data[0:len(data) - 1])
            elif len(parts) is 2:
                # Format is mm:ss
                seconds = 60* int(parts[0]) + int(parts[1])
            elif len(parts) is 3:
                # Format is hh:mm:ss
                seconds = 3600 * int(parts[0]) + 60 * int(parts[1]) + int(parts[2])

            # TODO: If its already in the map, throw exception?
            self.handle_person(self.person, seconds)
            self.count = self.count + 1
            self.state = self.State.INITIAL
            return

        if self.state is self.State.FOUND_PERSON:
            self.person = data
            self.state = self.state.SET_PERSON

class TimeMapSegmentHTMLParser(SegmentHTMLParser):
    def __init__(self, time_map, config):
        self.time_map = time_map
        super().__init__(config)

    def handle_person(self, person, seconds):
        self.time_map[person] = seconds

class SegmentCrawler():
    def __init__(self, cookie_file):
        self.cookie_file = cookie_file

    def crawl(self, segment_id, option, parser_factory):
        page_number = 1
        count = 0
        while True:
            segment_url = "https://www.strava.com/segments/{}?partial=true&{}&page={}&per_page=100".format(segment_id, option, page_number)
            print("Processing URL: " + segment_url)

            completed = subprocess.run(["curl", "--cookie", self.cookie_file, segment_url], capture_output=True)
            parser = parser_factory.new()
            parser.feed(completed.stdout.decode("utf-8"))

            # Processed everything
            if (parser.count < 100 * page_number): break

            page_number = page_number + 1
            count = parser.count


class SegmentStatisticsAggregator():
    class TimeMapSegmentHTMLParserFactory():
        def __init__(self,  config, time_map):
            self.time_map = time_map
            self.config = config

        def new(self):
            return TimeMapSegmentHTMLParser(self.time_map, self.config)

    def __init__(self,  segment, collected_data, config, run_config):
         self.segment = segment
         self.collected_data = collected_data
         self.config = config
         self.run_config = run_config

    def _get_time_map(self):
        time_map = {}

        parser_factory = self.TimeMapSegmentHTMLParserFactory(self.config, time_map)
        crawler = SegmentCrawler(self.config.cookie_file)
        for option in self.run_config.options:
            crawler.crawl(self.segment, option, parser_factory)

        return time_map

    def run(self):
        time_map = self._get_time_map()

        rankings = [(k, v) for k, v in time_map.items()]
        rankings.sort(key=(lambda a : a[1]))
        count = 0

        for (name, _) in rankings:
            if (count >= len(self.config.points)):
                thispoints = self.config.unmatched_participation_points
            else:
                thispoints = self.config.participation_points + self.config.points[count]

            if (name in self.collected_data.rankings):
                self.collected_data.rankings[name] = self.collected_data.rankings[name] + thispoints
                self.collected_data.segment_count[name] = self.collected_data.segment_count[name] + 1
            else:
                self.collected_data.rankings[name] = thispoints
                self.collected_data.segment_count[name] = 1

            count = count + 1

class Config():
    class RunConfig():
        def __init__(self, run_config_dict):
            self.output_file = run_config_dict["output_file"]
            self.options = run_config_dict["options"]

    def __init__(self, json_config, cookie_file):
        self.cookie_file = cookie_file
        self.segments = json_config["segments"]
        self.points = json_config["points"]
        self.participation_points = json_config["participation_points"]
        self.unmatched_participation_points = json_config["unmatched_participation_points"]
        runs = json_config["runs"]
        self.run_configs = []
        for run in runs:
            self.run_configs.append(self.RunConfig(run))


def main():
    config_file = open(sys.argv[1], "r")
    config_file_contents = config_file.read()
    json_config = json.loads(config_file_contents)
    cookie_file = sys.argv[2]
    config = Config(json_config, cookie_file)

    for run_config in config.run_configs:
        collected_data = CollectedData._make([{}, {}])
        for segment in config.segments:
            aggregator = SegmentStatisticsAggregator(segment, collected_data, config, run_config)
            aggregator.run()

        finalrankings = [(k, v) for k, v in collected_data.rankings.items()]
        finalrankings.sort(reverse=True, key=(lambda a : a[1]))
        with open(run_config.output_file, 'w') as file:
            for person, points in finalrankings:
                file.write(person + "," + str(points) + "," + str(collected_data.segment_count[person]) + "\n")

if __name__ == "__main__":
    main()
