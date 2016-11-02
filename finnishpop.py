#!/usr/bin/env python
# encoding: utf-8
"""
Scraper to tweet the population of Finland
"""
from __future__ import print_function
import argparse
from bs4 import BeautifulSoup  # pip install BeautifulSoup4
import re
import sys
import twitter
import urllib2
import webbrowser
import yaml

HELSINKI_LAT = 60.170833
HELSINKI_LONG = 24.9375


def population():
    url = "http://vrk.fi/"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page.read(), "lxml")

    # <div class="population-banner">
    #     <a href="/default.aspx?site=3&amp;docid=169">
    #         <h3>Suomen väkiluku</h3>
    #         <p>5 458 753</p>
    #     </a>
    # </div>

    # <div class="portlet-boundary portlet-boundary_populationdisplay_WAR_populationdisplayportlet_ portlet-static portlet-static-end portlet-borderless population-display-portlet " id="p_p_id_populationdisplay_WAR_populationdisplayportlet_">
    #   <span id="p_populationdisplay_WAR_populationdisplayportlet"></span>
    #   <div class="portlet-borderless-container" style="">
    #     <div class="portlet-body">
    #       <p><span><em>Suomen</em> väkiluku</span> 5&nbsp;507&nbsp;187</p>
    #     </div>
    #   </div>
    # </div>

    banner_div = soup.find_all("div", class_="population-display-portlet")[0]
    population = banner_div.div.div.p
    # get rid of <span> and contents
    population.span.decompose()
    # strip leading space, replace non-breaking space with standard space
    population = population.text.strip().replace(u'\xa0', " ")
    print(population)
    return population


# TODO call it
def validate(pop):
    if not pop:
        return False
    elif len(pop) < 7:  # population is at least 5000000
        return False
    elif re.match(r'\d[\d ]+\d', pop):
        return True
    return False


def load_yaml(filename):
    """
    File should contain:
    consumer_key: TODO_ENTER_YOURS
    consumer_secret: TODO_ENTER_YOURS
    oauth_token: TODO_ENTER_YOURS
    oauth_token_secret: TODO_ENTER_YOURS
    """
    f = open(filename)
    data = yaml.safe_load(f)
    f.close()
    if not data.viewkeys() >= {
            'oauth_token', 'oauth_token_secret',
            'consumer_key', 'consumer_secret'}:
        sys.exit("Twitter credentials missing from YAML: " + filename)
    return data


def build_tweet(pop):
    tweet = "Population of Finland: " + str(pop)
    return tweet


def tweet_it(string, credentials):
    if len(string) <= 0:
        return

    # Create and authorise an app with (read and) write access at:
    # https://dev.twitter.com/apps/new
    # Store credentials in YAML file
    t = twitter.Twitter(auth=twitter.OAuth(
        credentials['oauth_token'],
        credentials['oauth_token_secret'],
        credentials['consumer_key'],
        credentials['consumer_secret']))

    print("TWEETING THIS:\n", string)

    if args.test:
        print("(Test mode, not actually tweeting)")
    else:
        result = t.statuses.update(
            status=string,
            lat=HELSINKI_LAT, long=HELSINKI_LONG,
            display_coordinates=True)
        url = "http://twitter.com/" + \
            result['user']['screen_name'] + "/status/" + result['id_str']
        print("Tweeted:\n" + url)
        if not args.no_web:
            webbrowser.open(url, new=2)  # 2 = open in a new tab, if possible


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scraper to tweet the population of Finland",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-y', '--yaml',
        default='/Users/hugo/Dropbox/bin/data/finnishpop.yaml',
        help="YAML file location containing Twitter keys and secrets")
    parser.add_argument(
        '-nw', '--no-web', action='store_true',
        help="Don't open a web browser to show the tweeted tweet")
    parser.add_argument(
        '-x', '--test', action='store_true',
        help="Test mode: go through the motions but don't tweet anything")
    args = parser.parse_args()

    pop = population()
    print(pop)

    twitter_credentials = load_yaml(args.yaml)

    tweet = build_tweet(pop)

    print("Tweet this:\n", tweet)
    tweet_it(tweet, twitter_credentials)

# End of file
