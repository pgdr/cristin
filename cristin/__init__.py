import sys
from collections import namedtuple as T
import requests

BASEURL = "https://api.cristin.no/v2/"


def get(what):
    res = requests.get(what)
    res.raise_for_status()
    return res.json()


Person = T("Person", "first_name surname url cristin_person_id")


class Contribution:
    def __init__(self, contr):
        self._type = contr["category"].get("code", "N/A")
        self._year = contr.get("year_published")
        self._title = contr["title"].get("en", contr["title"].get("no"))
        self._url = contr.get("links", [{}])[0].get("url", "")
        self._journal = contr.get("journal", {}).get("name")
        self._contributors = contr["contributors"].get("preview", "N/A")
        self._result_id = contr["cristin_result_id"]


def make_person(first_name, surname, url=None, cristin_person_id=None):
    return Person(first_name, surname, url, cristin_person_id)


def str_person(person):
    name = person.first_name + " " + person.surname
    if person.cristin_person_id:
        name += f" ({person.cristin_person_id})"
    if person.url:
        name += f" [{person.url}]"
    return name


Person.__str__ = str_person


def results(person_id, institution=""):
    per_page = 300
    url = BASEURL + f"results?contributor={person_id}&per_page={per_page}"
    for r in get(url):
        yield Contribution(r)


def search_person(name, institution=""):
    namestr = "+".join(name.strip().split())
    if institution:
        url = BASEURL + f"persons/?name={namestr}&institution={institution}"
    else:
        url = BASEURL + f"persons/?name={namestr}"
    res = get(url)
    return [make_person(**p) for p in res]


def person(cristin_person_id):
    url = BASEURL + f"persons/{cristin_person_id}"
    return get(url)


def print_contribution(contr):
    print("Type         ", contr._type)
    print("Year         ", contr._year)
    print("Title        ", contr._title)
    print("URL          ", contr._url)
    print("Journal      ", contr._journal)
    print(
        "Contributors ", ", ".join([str(make_person(**c)) for c in contr._contributors])
    )
    print("result_id    ", contr._result_id)


def exit_with_usage():
    print("Usage: cristin --person Firstname Surname")
    print("Usage: cristin --person Firstname Surname @ UiB")
    print("       cristin --results cristin_person_id")
    sys.exit(1)


def run(command, argument):
    if command == "person":
        institution = ""
        if "@" in argument:
            argument, institution = [s.strip() for s in argument.split("@")]
        print(search_person(argument, institution=institution))
    elif command == "results":
        for res in sorted(results(argument), key=lambda x: x._year, reverse=True):
            print_contribution(res)
            print("\n")
    else:
        exit("Unknown command")


def main():
    if len(sys.argv) < 2:
        exit_with_usage()
    if sys.argv[1] not in ("--person", "--results"):
        exit_with_usage()
    command = sys.argv[1][2:]
    rest = " ".join(sys.argv[2:])
    run(command, rest)


if __name__ == "__main__":
    main()
