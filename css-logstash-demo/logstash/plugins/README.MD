Logstash S3 plugins do not support custom endpoints for other S3 installations
apart from AWS. The required patches are not included into the main development
branch.

Thus, we had to comopile the Logstash S3 plugins from the following branches:
# S3 input:
  At the moment, you need to apply a pull request to the main branch
  git clone https://github.com/logstash-plugins/logstash-input-s3
  git fetch origin pull/117/head:CUSTOM-ENDPOINT
  git checkout CUSTOM-ENDPOINT

# S3 output:
  https://github.com/gaul/logstash-output-s3/tree/custom-endpoint 
