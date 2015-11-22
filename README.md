# Marlon.io
UCPD data

Currently, the only functionality is extraction of raw data at `/api/detail/<dataset_name>'

Filters can be added specific to each of the three datasets `incidents`, `traffic_stops`, and `field_interviews'. For example:
```/api/detail/incidents?time1=010000&time2=150000&comments=disturbance
```
searches the `incidents` dataset for all records which occurred between 1:00 AM and 3:00 PM, and whose "comments" field contains the word disturbance (not case sensitive).
