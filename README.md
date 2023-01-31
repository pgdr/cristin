# Cristin API

This project is in no way affiliated with cristin.no.

It uses [api.cristin.no](https://api.cristin.no/v2/doc/index.html).

You may install it from [PyPI](https://pypi.org/project/cristin):

`pip install cristin`


## Person

This script can search for a person:

`cristin --person Firstname Surname`

You can also limit search to a specific institution with `@`:

`cristin --person Firstname Surname @ uib`


## Results

Once you have a person's `cristin_person_id`, you can query their results:

`cristin --results 1234`

You can put a limit to how many results you want by appending the limit.

`cristin --results 1234 3`


If you want to get a `csv` output, simply use `cristin --csv --results 1234 3`

## Results by person

If you want to combine the two above, use

`cristin --resultsby firstname surname --csv`
