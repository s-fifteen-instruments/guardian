#!/bin/sh
# Justin, 2022-07-01
#
# watcher seems to require notify.pipe to be up before starting,
# but the Compose option of conditional 'depends_on' works only for
# Compose >= 3.9 or < 3.0.
#
# Alternative suggested in 'https://docs.docker.com/compose/startup-order/'
# to implement a 'wait-for-it.sh' equivalent script to prepend in CMD.
set -e

# Retrieve required parameters
PIPE="$1"
shift

# Repeatedly check existence of file
# For host environment, use docker exec -it "$SERVICE" sh -c "test -p $PIPE"
until [ -p $PIPE ]; do
        >&2 echo "Notification pipe not up - sleeping..."
        sleep 1
done
>&2 echo "Notification pipe up!"
sleep 60 # Process whatever is in the pipe first
# Flush all unread epochs into pipe.
ls /epoch_files | grep -v notify.pipe > /epoch_files/notify.pipe
sleep 30
exec "$@"

