Plotting L1Calo Tower Defs
==========================

If you're here, you want to run the scripts. You will need this python code as well as

- `IdDictCalorimeter_DC3-05.xml`
- `gTowerInfo.txt`
- `jTowerInfo.txt`

files in the same location that `parse.py <parse.py>`_ is found. Then simply running::

    python parse.py

will produce the same PDFs you're looking at.

Installing
----------

To install, I set up a `virtual environment <https://virtualenvwrapper.readthedocs.org/en/latest/>`_ and then `pip install` the requirements::

    git clone https://www.github.com/kratsg/l1calo_tower_mappings
    cd l1calo_tower_mappings
    mkvirtualenv l1calo_tower_mappings
    pip install -r requirements.txt

and then whenever I go back to it in a new session, I simply need to do::

    cd l1calo_tower_mappings
    workon l1calo_tower_mappings

and I'm good to go.

Acknowledgements
================

Thanks to W. Hopkins for providing the files.
