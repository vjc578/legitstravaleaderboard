from html.parser import HTMLParser
import sys
import subprocess

points = [35, 30, 27, 24, 22, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
segments = ["https://www.strava.com/segments/18009162",
"https://www.strava.com/segments/12602205",
"https://www.strava.com/segments/847877",
"https://www.strava.com/segments/13164122",
"https://www.strava.com/segments/24963500",
"https://www.strava.com/segments/9430536",
"https://www.strava.com/segments/18869214",
"https://www.strava.com/segments/19420518",
"https://www.strava.com/segments/19845029",
"https://www.strava.com/segments/13916096",
"https://www.strava.com/segments/3977014",
"https://www.strava.com/segments/24895515",
"https://www.strava.com/segments/917649",
"https://www.strava.com/segments/21553796",
"https://www.strava.com/segments/13893599",
"https://www.strava.com/segments/16571671",
"https://www.strava.com/segments/3153417",
"https://www.strava.com/segments/24736806",
"https://www.strava.com/segments/12421407",
"https://www.strava.com/segments/24969638",
"https://www.strava.com/segments/8340561",
"https://www.strava.com/segments/21763226",
"https://www.strava.com/segments/20469732",
"https://www.strava.com/segments/15791170",
"https://www.strava.com/segments/19133193",
"https://www.strava.com/segments/24981311",
"https://www.strava.com/segments/17044098",
"https://www.strava.com/segments/9084546",
"https://www.strava.com/segments/3586828",
"https://www.strava.com/segments/1358498",
"https://www.strava.com/segments/2749245",
"https://www.strava.com/segments/24970098",
"https://www.strava.com/segments/24969607",
"https://www.strava.com/segments/9375224",
"https://www.strava.com/segments/10492069",
"https://www.strava.com/segments/12057667",
"https://www.strava.com/segments/3715474",
"https://www.strava.com/segments/4341250",
"https://www.strava.com/segments/10821433",
"https://www.strava.com/segments/12727610",
"https://www.strava.com/segments/7746545",
"https://www.strava.com/segments/12452468",
"https://www.strava.com/segments/9424327",
"https://www.strava.com/segments/24983019",
"https://www.strava.com/segments/24895619",
"https://www.strava.com/segments/2869589",
"https://www.strava.com/segments/2567785",
"https://www.strava.com/segments/23116240",
"https://www.strava.com/segments/1365197",
"https://www.strava.com/segments/24627589",
"https://www.strava.com/segments/13861791",
"https://www.strava.com/segments/24983881",
"https://www.strava.com/segments/24984157",
"https://www.strava.com/segments/24992170",
"https://www.strava.com/segments/24963518",
"https://www.strava.com/segments/1367485",
"https://www.strava.com/segments/15952592",
"https://www.strava.com/segments/16959203",
"https://www.strava.com/segments/10735790",
"https://www.strava.com/segments/24992781",
"https://www.strava.com/segments/2743341",
"https://www.strava.com/segments/14645040",
"https://www.strava.com/segments/20501792",
"https://www.strava.com/segments/16433409",
"https://www.strava.com/segments/14058810",
"https://www.strava.com/segments/4031142",
"https://www.strava.com/segments/6823502",
"https://www.strava.com/segments/24414054",
"https://www.strava.com/segments/1611860",
"https://www.strava.com/segments/18152742",
"https://www.strava.com/segments/5524719",
"https://www.strava.com/segments/887503",
"https://www.strava.com/segments/12793300",
"https://www.strava.com/segments/21393535",
"https://www.strava.com/segments/4961685",
"https://www.strava.com/segments/24977520",
"https://www.strava.com/segments/10326770",
"https://www.strava.com/segments/7770278",
"https://www.strava.com/segments/13296676",
"https://www.strava.com/segments/1237021",
"https://www.strava.com/segments/13915990",
"https://www.strava.com/segments/5177031",
"https://www.strava.com/segments/1865121",
"https://www.strava.com/segments/25093766",
"https://www.strava.com/segments/5397534",
"https://www.strava.com/segments/10747924",
"https://www.strava.com/segments/5955218",
"https://www.strava.com/segments/7039851",
"https://www.strava.com/segments/4009884",
"https://www.strava.com/segments/12244391",
"https://www.strava.com/segments/24969568"]

rankings = {}

class MyHTMLParser(HTMLParser):
    def __init__(self, url):
        self.foundTrackClick = False
        self.foundPerson = False
        self.count = 0
        self.url = url
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
            if (self.count >= len(points)):
              thispoints = 10
            else:
              thispoints = 10 + points[self.count]

            if (data in rankings):
                rankings[data] = rankings[data] + thispoints
            else:
                rankings[data] = thispoints
            self.count = self.count + 1
            self.foundPerson = False



def main():
    gender=""
    if (len(sys.argv) > 1 and sys.argv[1] == '-w'):
        gender="&gender=F"

    for segment in segments:
        segment_url = segment + "?filter=overall&page=1&per_page=100&partial=true&date_range=this_month" + gender
        completed = subprocess.run(["curl", "--cookie", "/Users/vjc/Downloads/cookies2.txt", segment_url], capture_output=True)
        parser = MyHTMLParser(segment_url)
        parser.feed(completed.stdout.decode("utf-8"))

    finalrankings = [(k, v) for k, v in rankings.items()]
    finalrankings.sort(reverse=True, key=(lambda a : a[1]))
    for person, points in finalrankings:
        print(person + "," + str(points))

if __name__ == "__main__":
    main()
