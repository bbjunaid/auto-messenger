# auto-messenger
Auto messaging for a social network

- Setup virtualenv:

    ./scripts/setup.sh
  
- Activate virtualenv:

    . virtualenv/bin/activate
  
- Fill the private_const.py

    private_const.py

- Install PhantomJS and Redis and run redis as deamon:

    brew install phantomjs
    brew install redis
    /usr/local/bin/redis-server --daemonize yes
    
- Setup DyanmoDB in aws with a 'members' table and primary key 'uid'

- Store aws credentials in a file:

    ~/.aws/credentials

- Run the scripts:

    python crawler.py
    python messenger.py
    python replier.py

Future work:
- Add location library to store nearest major city
- Incorporate machine learning/NLP based on pictures and messages
