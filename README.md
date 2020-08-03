# Strava Challenge Leaderboard Creator

### Overview

Welcome to the segment leaderboard creator, the best tool ever for creating leaderboards during segment challenges. What's that you say? I should be using Strava APIs instead of parsing HTML and copying cookie files from a browser? Sounds great! Let me just check ... oops [looks like NO](https://www.dcrainmaker.com/2020/05/strava-cuts-off-leaderboard-for-free-users-reduces-3rd-party-apps-for-all-and-more.html)

So yeah, in the absence of doing things in a proper way, I wrote this instead! The goal of this tool is to create a leaderboard for segment challenges. These are events where riders ride a variety of segments. Each rider is given a certain number of points depending on their place on the segment. The total on all segments is then summed to get the total points for each rider. Then we sort by total, and voila, leaderboard. 

### Config File

The tool takes as input a JSON configuration file with a list of segments and configuration options. It allows for multiple runs, that is, different outputs with different options. The options as currently specified are just arguments appended to the segment URL. So for example "filter=overall&date_range=this_month&gender=F" says "Give me the overall leaderboard for this month for females"

Take a look at the august_neighborhood_segment_challenge.txt file in the examples folder for more details

### Cookie File

The cookie file is in standard [netscape/mozilla format](https://xiix.wordpress.com/2006/03/23/mozillafirefox-cookie-format/). You'll need to install the [cookies.txt chrome extension](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg?hl=en) to get this information

### Steps to run the program

This assumes you have the cookies.txt chrome extension and python installed

1. Open strava.com and login if you haven't
2. Open the cookies.txt extension and download the cookies for that page, let's call it "stravacookies.txt"
3. Run the program `python leaderboard.py examples/august_neighborhood_segment_challenge.txt stravacookies.txt`
4. Bask in the glory of your fully armed and operation leaderboard.



