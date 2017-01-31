# auto-messenger
Auto messaging for a social network

Setup virtualenv:

    ./scripts/setup.sh
  
Activate virtualenv:

    . virtualenv/bin/activate
  
Fill the private_const.py

    private_const.py

Install PhantomJS and Redis and run redis as deamon:

    brew install phantomjs
    brew install redis
    /usr/local/bin/redis-server --daemonize yes

Run the script:

    python messenger.py
