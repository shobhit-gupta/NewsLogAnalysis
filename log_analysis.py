#!/usr/bin/env python

from __future__ import print_function
from os import system
import sys
import psycopg2


DBNAME = 'news'
COLUMNS = 64
REPORT_TITLE = 'Log Analysis Report'


class console_style:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


queries = [
    {
        'query': """
            SELECT title,
                   count(path)
              FROM articles
                   LEFT JOIN log
                   ON '/article/' || slug = path
             GROUP BY title
             ORDER BY count DESC
             LIMIT 3;
            """,
        'title': 'What are the most popular three articles of all time?',
        'to_string': lambda results:
            '\n'.join(['"{}" - {} views'.format(r[0], r[1]) for r in results])
    },

    {
        'query': """
            SELECT (SELECT name
                      FROM authors
                     WHERE authors.id = author),
                   count(path)
              FROM articles
                   LEFT JOIN log
                   ON '/article/' || slug = path
             GROUP BY author
             ORDER BY count DESC;
            """,
        'title': 'Who are the most popular authors of all time?',
        'to_string': lambda results:
            '\n'.join(['{} - {} views'.format(r[0], r[1]) for r in results])
    },

    {
        'query': """
            SELECT TO_CHAR(day, 'FMMonth DD, YYYY'),
                   ROUND(error_rate, 2)
              FROM (SELECT SUM(CASE
                               WHEN status LIKE '4%' THEN 1
                               END) * 100.0 / count(*) AS error_rate,
                           DATE(time) AS day
                      FROM log
                     GROUP BY day) AS temp
             WHERE error_rate > 1;
            """,
        'title': 'On which days did more than 1% of requests lead to errors?',
        'to_string': lambda results:
            '\n'.join(['{} - {}% errors'.format(r[0], r[1]) for r in results])
    }
]


def print_report_title(title):
    """Helper function for print_report function"""
    print(console_style.UNDERLINE
          + console_style.HEADER
          + console_style.BOLD
          + title.upper()
          + console_style.ENDC)
    print('\n')


def print_query_title(title):
    """Helper function for print_report function"""
    print(console_style.BOLD
          + console_style.UNDERLINE
          + title
          + console_style.ENDC)


def print_pre_query_msg():
    """Helper function for print_report function"""
    print('Processing...', end='')
    sys.stdout.flush()


def print_post_query_result(result):
    """Helper function for print_report function"""
    print('\r' + result)
    print('\n')


def print_report():
    """Main function to print the log analysis report"""
    # Prep console for printing the report.
    system('clear')
    print_report_title(REPORT_TITLE)

    # Connect to the database
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()

    # Execute & report on each query
    for q in queries:
        print_query_title(q['title'])
        print_pre_query_msg()
        c.execute(q['query'])
        r = c.fetchall()
        print_post_query_result(q['to_string'](r))

    # Close the connection to the database
    db.close()


if __name__ == "__main__":
    print_report()
