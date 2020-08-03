from html.parser import HTMLParser
from collections import namedtuple
import sys
import subprocess
import json

CollectedData = namedtuple('Data', 'rankings, segment_count')

class SegmentHTMLParser(HTMLParser):
    def __init__(self, initial_count, collected_data, config):
        self.foundTrackClick = False
        self.foundPerson = False
        self.count = initial_count
        self.collected_data = collected_data
        self.config = config
        super().__init__()

    def handle_starttag(self, tag, attrs):
      if (self.foundTrackClick and tag == 'a'):
          self.foundPerson = True
          self.foundTrackClick = False

      if tag == 'td':
        for attr in attrs:
            if (len(attr) >= 2 and attr[0] == "class" and attr[1] == "athlete track-click"):
                self.foundTrackClick = True

    def handle_data(self, data):
        if (self.foundPerson):
            if (self.count >= len(self.config.points)):
              thispoints = self.config.unmatched_participation_points
            else:
              thispoints = self.config.participation_points + self.config.points[self.count]

            if (data in self.collected_data.rankings):
                self.collected_data.rankings[data] = self.collected_data.rankings[data] + thispoints
                self.collected_data.segment_count[data] = self.collected_data.segment_count[data] + 1
            else:
                self.collected_data.rankings[data] = thispoints
                self.collected_data.segment_count[data] = 1
            self.count = self.count + 1
            self.foundPerson = False

class SegmentCrawler():
    def __init__(self,  segment_url, collected_data, config):
         self.segment_url = segment_url
         self.collected_data = collected_data
         self.config = config

    def run(self):
        page_number = 1
        count = 0
        while True:
            segment_url = self.segment_url + "&page={}&per_page=100".format(page_number)
            print("Processing URL: " + segment_url)

            completed = subprocess.run(["curl", "--cookie", self.config.cookie_file, segment_url], capture_output=True)
            parser = SegmentHTMLParser(count, self.collected_data, self.config)
            parser.feed(completed.stdout.decode("utf-8"))

            # Processed everything
            if (parser.count < 100 * page_number): break

            page_number = page_number + 1
            count = parser.count


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
            segment_url = segment + "?partial=true&" + run_config.options
            crawler = SegmentCrawler(segment_url, collected_data, config)
            crawler.run()

        finalrankings = [(k, v) for k, v in collected_data.rankings.items()]
        finalrankings.sort(reverse=True, key=(lambda a : a[1]))
        with open(run_config.output_file, 'w') as file:
            for person, points in finalrankings:
                file.write(person + "," + str(points) + "," + str(collected_data.segment_count[person]) + "\n")

if __name__ == "__main__":
    main()
