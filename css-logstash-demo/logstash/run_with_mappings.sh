#
# The entrypoint for logstash checks for the existence of required
# mappings in elasticsearch and 
#
# A similar approch can be taken for any case where an initial setup after
# installation at runtime is required, e.g. for database schema upload
#
# Do NOT use entrypoints for commands that can run already at image creation
# time, e.g the creation of required users!
#

####
# Mappings
curl -s -XPUT http://elastiksearch.elk:${ELASTICSEARCH_SERVICE_PORT}/shakespeare?pretty -H 'Content-Type: application/json' -d'
{
 "mappings" : {
  "_default_" : {
   "properties" : {
    "speaker" : {"type": "keyword" },
    "play_name" : {"type": "keyword" },
    "line_id" : { "type" : "integer" },
    "speech_number" : { "type" : "integer" }
   }
  }
 }
}
'

curl -s -XPUT http://elasticsearch.elk:${ELASTICSEARCH_SERVICE_PORT}/logstash-2015.05.18?pretty -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "log": {
      "properties": {
        "geo": {
          "properties": {
            "coordinates": {
              "type": "geo_point"
            }
          }
        }
      }
    }
  }
}
'

curl -s -XPUT http://elasticsearch.elk:${ELASTICSEARCH_SERVICE_PORT}/logstash-2015.05.19?pretty -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "log": {
      "properties": {
        "geo": {
          "properties": {
            "coordinates": {
              "type": "geo_point"
            }
          }
        }
      }
    }
  }
}
'

curl -s -XPUT http://elasticsearch.elk:${ELASTICSEARCH_SERVICE_PORT}/logstash-2015.05.20?pretty -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "log": {
      "properties": {
        "geo": {
          "properties": {
            "coordinates": {
              "type": "geo_point"
            }
          }
        }
      }
    }
  }
}
'

./docker-entrypoint
