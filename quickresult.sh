#!/bin/bash

if [ -f /usr/local/bin/gshuf ]; then
    # Mac: brew install coreutils
    SHUF=/usr/local/bin/gshuf
else
    SHUF=shuf
fi

for i in `seq 1 20` ; do
    ADJ=`$SHUF adjective.txt | head -n1`
    NOUN=`$SHUF noun.txt | head -n1`
    echo -n $ADJ
    echo -n ' '
    echo $NOUN
done

