import sys
from collections import namedtuple as T
import requests
from pydantic import BaseModel
from typing import Optional

BASEURL = "https://api.cristin.no/v2/"


def get(what):
    res = requests.get(what)
    res.raise_for_status()
    return res.json()


class Person(BaseModel):
    cristin_person_id: Optional[int] = None
    first_name: str
    surname: str
    url: Optional[str] = None

    def __str__(self):
        name = self.first_name + " " + self.surname
        if self.cristin_person_id:
            name += f" ({self.cristin_person_id})"
        if self.url:
            name += f" [{self.url}]"
        return name


class Contribution:
    def __init__(self, contr):
        self._type = contr["category"].get("code", "N/A")
        self._year = contr.get("year_published")
        self._title = contr["title"].get("en", contr["title"].get("no"))
        self._url = contr.get("links", [{}])[0].get("url", "")
        self._journal = contr.get("journal", {}).get("name")
        self._contributors = contr["contributors"].get("preview", "N/A")
        self._result_id = contr["cristin_result_id"]


def _csv_safe(val):
    _illegal = "\n\r"
    val = str(val).strip()
    while set(_illegal).intersection(set(val)):
        val = val.replace("\n", " ")
        val = val.replace("\r", " ")
        val = val.strip()
    if "," in val:
        return f'"{val}"'
    return val


def csv_header():
    return "type,year,title,url,journal,contributors,result_id"


def csv_contribution(contr):
    return ",".join(
        map(
            _csv_safe,
            [
                contr._type,
                contr._year,
                contr._title,
                contr._url,
                contr._journal,
                ", ".join([str(Person(**c)) for c in contr._contributors]),
                contr._result_id,
            ],
        )
    )


def results(person_id, per_page=None):
    if per_page is None:
        per_page = 10
    url = (
        BASEURL
        + f"results?contributor={person_id}&per_page={per_page}&sort=year_published desc"
    )
    for r in get(url):
        yield Contribution(r)


def search_person(name, institution=""):
    namestr = "+".join(name.strip().split())
    if institution:
        url = BASEURL + f"persons/?name={namestr}&institution={institution}"
    else:
        url = BASEURL + f"persons/?name={namestr}"
    res = get(url)
    return [Person(**p) for p in res]


def get_person(cristin_person_id):
    url = BASEURL + f"persons/{cristin_person_id}"
    return get(url)


def print_contribution(contr):
    print("Type         ", contr._type)
    print("Year         ", contr._year)
    print("Title        ", contr._title)
    print("URL          ", contr._url)
    print("Journal      ", contr._journal)
    print("Contributors ", ", ".join([str(Person(**c)) for c in contr._contributors]))
    print("result_id    ", contr._result_id)


def exit_with_usage():
    print("Usage: cristin --person Firstname Surname")
    print("       cristin --person Firstname Surname @ UiB")
    print("       cristin --results cristin_person_id")
    print("       cristin --results cristin_person_id [limit]", end="")
    print(" # number of entries (default 10), e.g.")
    print("       cristin --results cristin_person_id 100")
    sys.exit(1)


def run_person(argument):
    institution = ""
    if "@" in argument:
        argument, institution = [s.strip() for s in argument.split("@")]
    for p in search_person(argument, institution=institution):
        print(p)


def run_results(argument, csv=False):
    limit = None
    if " " in argument.strip():
        argument, limit = argument.strip().split()
    retval = results(argument, limit)
    if csv:
        print(csv_header())
    for res in sorted(retval, key=lambda x: x._year, reverse=True):
        if csv:
            print(csv_contribution(res))
        else:
            print_contribution(res)
            print("\n")


def run_resultsby(argument, csv=False):
    person = search_person(argument)
    if len(person) != 1:
        exit(f"Could not find unique person: {person}")
    pid = person[0].cristin_person_id
    retval = results(pid, 100)
    if csv:
        print(csv_header())
    for res in sorted(retval, key=lambda x: x._year, reverse=True):
        if csv:
            print(csv_contribution(res))
        else:
            print_contribution(res)
            print("\n")


def run(command, argument, csv=False):
    if command == "person":
        run_person(argument)
    elif command == "results":
        run_results(argument, csv=csv)
    elif command == "resultsby":
        run_resultsby(argument, csv=csv)
    else:
        exit("Unknown command")


def main():
    csv = False
    if "--csv" in sys.argv:
        csv = True
        sys.argv.remove("--csv")
    if len(sys.argv) < 2 or "-h" in sys.argv[1]:
        exit_with_usage()
    if sys.argv[1] not in ("--person", "--results", "--resultsby"):
        print(f'Unknown command "{sys.argv[1]}"')
        exit_with_usage()
    command = sys.argv[1][2:]
    rest = " ".join(sys.argv[2:])
    run(command, rest, csv=csv)


if __name__ == "__main__":
    main()
