from html.parser import HTMLParser
import sys
import subprocess
import json

class SegmentHTMLParser(HTMLParser):
    def __init__(self, rankings, segment_count, points, participation_points, unmatched_participation_points):
        self.foundTrackClick = False
        self.foundPerson = False
        self.count = 0
        self.rankings = rankings
        self.segment_count = segment_count
        self.points = points
        self.participation_points = participation_points
        self.unmatched_participation_points = unmatched_participation_points
        super().__init__()

    def handle_starttag(self, tag, attrs):
      if (self.foundTrackClick and tag == 'a'):
          self.foundPerson = True
          self.foundTrackClick = False

      if tag == 'td':
        for attr in attrs:
            if (attr[0] == "class" and attr[1] == "athlete track-click"):
                self.foundTrackClick = True

    def handle_data(self, data):
        if (self.count >= 100): raise Exception('Too many entries!')
        if (self.foundPerson):
            if (self.count >= len(self.points)):
              thispoints = self.unmatched_participation_points
            else:
              thispoints = self.participation_points + self.points[self.count]

            if (data in self.rankings):
                self.rankings[data] = self.rankings[data] + thispoints
                self.segment_count[data] = self.segment_count[data] + 1
            else:
                self.rankings[data] = thispoints
                self.segment_count[data] = 1
            self.count = self.count + 1
            self.foundPerson = False

class SegmentCrawler():
    def __init__(self, cookie_file, segment_url, rankings, segment_count, points, participation_points, unmatched_participation_points):
         self.cookie_file = cookie_file
         self.segment_url = segment_url
         self.rankings = rankings
         self.segment_count = segment_count
         self.points = points
         self.participation_points = participation_points
         self.unmatched_participation_points = unmatched_participation_points

    def run(self):
        page_number = 1
        while True:
            segment_url = self.segment_url + "&page={}&per_page=100".format(page_number)
            print("Processing URL: " + segment_url)

            completed = subprocess.run(["curl", "--cookie", self.cookie_file, segment_url], capture_output=True)
            parser = SegmentHTMLParser(self.rankings, self.segment_count, self.points, self.participation_points, self.unmatched_participation_points)
            parser.feed(completed.stdout.decode("utf-8"))

            # Processed everything
            if (parser.count < 100): break

            page_number = page_number + 1


class Config():
    class RunConfig():
        def __init__(self, output_file, options):
            self.output_file = output_file
            self.options = options

    def __init__(self, config_filename):
        f = open(config_filename, "r")
        contents = f.read()
        json_config = json.loads(contents)
        self.segments = json_config["segments"]
        self.points = json_config["points"]
        self.participation_points = json_config["participation_points"]
        self.unmatched_participation_points = json_config["unmatched_participation_points"]
        runs = json_config["runs"]
        self.run_configs = []
        for run in runs:
            self.run_configs.append(self.RunConfig(run["output_file"], run["options"]))


def main():
    config = Config(sys.argv[1])
    cookie_file = sys.argv[2]

    for run_config in config.run_configs:
        rankings = {}
        count = {}
        for segment in config.segments:
            segment_url = segment + "?partial=true&" + run_config.options
            crawler = SegmentCrawler(cookie_file, segment_url, rankings, count, config.points, config.participation_points, config.unmatched_participation_points)
            crawler.run()

        finalrankings = [(k, v) for k, v in rankings.items()]
        finalrankings.sort(reverse=True, key=(lambda a : a[1]))
        with open(run_config.output_file, 'w') as file:
            for person, points in finalrankings:
                file.write(person + "," + str(points) + "," + str(count[person]) + "\n")

if __name__ == "__main__":
    main()
