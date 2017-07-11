# coding=utf-8
import datetime
import os

from collections import namedtuple

import requests
from dateutil.relativedelta import relativedelta

repo = "conan-io/conan"
username = "lasote"
token = os.getenv("GH_TOKEN", "")


def get_issues(from_date, repo, user, key):
    Issue = namedtuple("issue", "created_at, state, comments")
    ret = {}
    iso_since = from_date.isoformat()
    for page in range(100):
        issues = requests.get("https://api.github.com/repos/%s/issues"
                              "?page=%d&since=%s&state=all" % (repo, page, iso_since), auth=(user, key))
        data = issues.json()
        if not data:
            break
        for issue in data:
            ret[issue["number"]] = Issue(issue["created_at"], issue["state"], issue["comments"])
    return ret


def write_cvs(rows, filename):
    import csv
    import os

    if os.path.exists(filename):
        os.unlink(filename)
    with open(filename, 'w') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        for row in rows:
            spamwriter.writerow(row)


def get_rows(init_date, end_date, repo, user, key):
    all_issues = get_issues(init_date, repo, user, key)

    tmp = init_date
    rows = []
    while tmp < end_date:
        tmp = tmp + delta
        num_open_issues = 0
        num_closed_issues = 0
        num_comments = 0
        for issue_id, issue in all_issues.items():
            import dateutil.parser
            created_at = dateutil.parser.parse(issue.created_at)
            if created_at.date() < (tmp + delta) and created_at.date() >= tmp:
                num_open_issues += 1 if issue.state == "open" else 0
                num_closed_issues += 1 if issue.state == "closed" else 0
                num_comments += issue.comments

        row = [tmp.isoformat(), str(num_open_issues), str(num_closed_issues), str(num_comments)]
        rows.append(row)
        print(row)
    return rows

if __name__ == "__main__":
    from datetime import timedelta
    init_date = datetime.date(2017, 1, 1)
    end_date = datetime.date(2017, 7, 31)
    delta = relativedelta(months=1)

    rows = get_rows(init_date, end_date, repo, username, token)

    write_cvs(rows, 'issues.csv')
