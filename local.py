import scrape, update

rows = scrape.fullScrape('09%2F01%2F2015', 'incidents')
update.updateTable('incidents', rows)

rows = scrape.fullScrape('09%2F01%2F2015', 'traffic_stops')
update.updateTable('traffic_stops', rows)

rows = scrape.fullScrape('09%2F01%2F2015', 'field_interviews')
update.updateTable('field_interviews', rows)
