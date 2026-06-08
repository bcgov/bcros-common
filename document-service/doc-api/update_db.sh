#! /bin/sh
COMMAND=${1:-upgrade}
REVISION=${2:-}
echo starting $COMMAND $REVISION
export DEPLOYMENT_ENV=migration
export PYTHONPATH=/code/src:$PYTHONPATH
export FLASK_APP=wsgi:app
cd /code
flask db $COMMAND $REVISION
echo 'upgrade completed'
