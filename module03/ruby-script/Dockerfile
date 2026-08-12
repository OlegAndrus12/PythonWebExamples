# Line for line the same shape as ../python-script/Dockerfile — only the base
# image and the interpreter changed. Try writing it yourself before reading it.

# find base image
FROM ruby:3.3-slim

# navigate to /app or any other you want
WORKDIR /app

# copy project files
COPY script.rb script.rb

# run the ruby script
CMD ["ruby", "script.rb"]
