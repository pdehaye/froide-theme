#!/bin/bash
pbundle-py manage.py compilemessages 2>&1
pbundle-py manage.py collectstatic --noinput  2>&1
#pbundle-py manage.py compress 2>&1

