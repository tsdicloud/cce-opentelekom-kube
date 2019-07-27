#
# Derive an image from the elastic base image (opensource version)
FROM docker.elastic.co/logstash/logstash:6.3.2

LABEL maintainer="Bernd Rederlechner <bernd.rederlechner@t-systems.com>" \
      tsystems.project="CCE Devops Tutorial" \
      tsystems.application="ELK OBS general purpose stack"

USER root

# extend entrypoint
COPY run_with_mappings.sh /usr/local/bin/
RUN chmod 0755 /usr/local/bin/run_with_mappings.sh

USER logstash

# install standard plugins from web
# patched plugins without verification
RUN bin/logstash-plugin install logstash-filter-json logstash-input-s3

# remove demo code
RUN rm -f /usr/share/logstash/pipeline/logstash.conf

# add pipelines
ADD pipeline/ /usr/share/logstash/pipeline/
ADD config/ /usr/share/logstash/config/

ENTRYPOINT ["/usr/local/bin/run_with_mappings.sh"] 

