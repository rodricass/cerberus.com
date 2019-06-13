##############################################################
### Cerberus installer 0.2                                 ###
### requires mongodb server installed                      ###
##############################################################

# Clones repo
echo downloading app data...
git clone https://github.com/galias11/cerberus.git
echo data downloaded

# setup app
echo running app setup
[ -x "$(command -v python3)" ] && PYTHON=python3 || PYTHON=python;
[ -x "$(command -v pip3)" ] && PIP=pip3 || PIP=pip;
cd cerberus
$PIP install --ignore-installed -r requirements.txt
$PYTHON -m spacy download es_core_news_md
$PYTHON ./manage.py collectstatic
cp ./scripts/config/web.main.config ../web.config
cp ./scripts/config/web.static.config ./static/web.config
$PYTHON ./manage.py migrate
$PYTHON ./scripts/nlp_setup.py
echo app setup successful
$PYTHON manage.py createsuperuser