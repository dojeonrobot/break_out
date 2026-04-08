#!/bin/bash
# cache-bust.sh: Add ?v=timestamp to all static asset references
TS=$1
DIR=$2
find "$DIR" \( -name '*.html' -o -name '*.css' \) -exec sed -i -E "s/\.(css|js|png|jpg|jpeg|mp3|m4a|pdf)([\"')])/.\1?v=${TS}\2/g" {} +
