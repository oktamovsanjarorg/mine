#!/bin/bash
set -euo pipefail

LOCALES_DIR="locales"
DOMAIN="messages"
LANGUAGES=("uz" "en" "ru")

echo "🌐 Generating locales..."

# 1. Extract messages
pybabel extract -F babel.cfg -o $LOCALES_DIR/$DOMAIN.pot .

# 2. Init or update catalogs
for lang in "${LANGUAGES[@]}"; do
    if [ -f "$LOCALES_DIR/$lang/LC_MESSAGES/$DOMAIN.po" ]; then
        echo "Updating catalog for $lang..."
        pybabel update -i $LOCALES_DIR/$DOMAIN.pot -d $LOCALES_DIR -D $DOMAIN -l $lang
    else
        echo "Initializing catalog for $lang..."
        pybabel init -i $LOCALES_DIR/$DOMAIN.pot -d $LOCALES_DIR -D $DOMAIN -l $lang
    fi
done

# 3. Compile catalogs
pybabel compile -d $LOCALES_DIR -D $DOMAIN

echo "✅ Locales generated and compiled."
