# -- MATERIALIZED VIEW -- Takes about 700ms on test machine.
"""
CREATE MATERIALIZED VIEW popular AS
(SELECT author as author,
       articles.id as article,
       count(log.path) as hits
  FROM articles 
       LEFT JOIN log
       ON ('/article/' || slug = log.path)
 GROUP BY articles.id, 
       author);
"""

# -- Query 1 -- Takes about 1ms compared to 700-800 ms as compared to
# non-optimized version.
"""
  SELECT (SELECT title
            FROM articles
           WHERE article = articles.id), 
         SUM(hits) as hits
    FROM popular
GROUP BY article
ORDER BY hits DESC
   LIMIT 3;
"""


# -- Query 2 -- Takes about 1ms compared to 700-800 ms as compared to
# non-optimized version.

# This is slightly faster on average than the one below that is based on join.
"""
SELECT (SELECT name 
          FROM authors 
         WHERE author = authors.id),
       SUM(hits) as hits
  FROM popular
 GROUP BY author
 ORDER BY hits desc;
"""

"""
SELECT name,
       SUM(hits) as hits
  FROM authors
       LEFT JOIN popular
       ON authors.id = popular.author
 GROUP BY authors.id
 ORDER BY hits DESC;
 """

 # -- Query 3 --
 # A much faster version is again possible by doing bulk of work once
 # and storing it in a materialized view which will be updated periodi-
 # -cally with delta changes which may be determined using the log id.