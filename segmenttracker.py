# This is hacky and needs to be cleaned up and moved. Break out stuff in leaderboard that
# is not leaderboard specific.

import sys
import leaderboard
import json

class SegmentTrackerHTMLParser(leaderboard.SegmentHTMLParser):
    def __init__(self, person_name, segment, found_segments, config):
        self.person_name = person_name
        self.segment = segment
        self.found_segments = found_segments
        super().__init__(config)

    def handle_person(self, person_name, seconds):
        if (person_name == self.person_name):
            self.found_segments.add(self.segment)

class SegmentTrackerHTMLParserFactory():
        def __init__(self, person, segment, found_segments, config):
            self.person = person
            self.segment = segment
            self.found_segments = found_segments
            self.config = config

        def new(self):
            return SegmentTrackerHTMLParser(self.person, self.segment, self.found_segments, self.config)

def main():
    config_file = open(sys.argv[1], "r")
    config_file_contents = config_file.read()
    json_config = json.loads(config_file_contents)
    cookie_file = sys.argv[2]
    config = leaderboard.Config(json_config, cookie_file)

    all_segments = set(config.segments)
    found_segments = set()

    for segment in all_segments:
        factory = SegmentTrackerHTMLParserFactory("Vinay Chaudhary", segment, found_segments, config)
        crawler = leaderboard.SegmentCrawler(cookie_file)
        crawler.crawl(segment, "filter=overall&date_range=this_month", factory)

    missing_segments = all_segments - found_segments
    print(",".join(missing_segments))


if __name__ == "__main__":
    main()
