"""The big-case board's short caption (:mod:`fedcourtsai.short_caption`).

Every caption below is a real `event.yaml` title from the committed ledger. The
expected value is what the rule produces, including every ``None``: the rule is
conservative by design, and a ``None`` pinned here is a claim that the rule
declines that caption, not a failure to reach it.
"""

import pytest

from fedcourtsai.short_caption import short_caption


@pytest.mark.parametrize(
    ("caption", "expected"),
    [
        # The sovereigns stand as written; officials are read by surname.
        (
            "Donald J. Trump, President of the United States, et al. v. California, et al.",
            "Trump v. California",
        ),
        ("United States v. E. Jean Carroll, et al.", "United States v. Carroll"),
        ("United States, et al. v. Nicolas Talbott, et al.", "United States v. Talbott"),
        ("Alabama, et al. v. California, et al.", "Alabama v. California"),
        ("Joseph J. Roybal, Sheriff, et al. v. Darlene Griffith", "Roybal v. Griffith"),
        ("Guam v. Richard Y. Ybanez, et al.", "Guam v. Ybanez"),
        (
            "Wes Allen, Alabama Secretary of State, et al. v. Marcus Caster, et al.",
            "Allen v. Caster",
        ),
        (
            "Jane Doe v. Robert F. Kennedy, Jr., Secretary of Health and Human Services",
            "Doe v. Kennedy",
        ),
        # A description after the name never reaches the short form, even one that
        # names an institution.
        (
            "Youth 71Five Ministries v. Charlene Williams, Individually and as Director of "
            + "Oregon Department of Education, et al.",
            "Youth 71Five Ministries v. Williams",
        ),
        # A name suffix is its own segment and is dropped.
        (
            "Eddie Grant, Jr., et al. v. Ronnell Higgins, in His Official Capacity as "
            + "Commissioner of the Connecticut Department of Emergency Services and Public "
            + "Transportation, et al.",
            "Grant v. Higgins",
        ),
        (
            "Benancio Garcia, III v. Steven Hobbs, Secretary of State of Washington, et al.",
            "Garcia v. Hobbs",
        ),
        # Corporate forms are dropped, whether inside the name or a segment after it.
        ("Apple Inc. v. Epic Games, Inc.", "Apple v. Epic Games"),
        ("Google LLC v. VirtaMove, Corp., et al.", "Google v. VirtaMove"),
        (
            "NHK Spring Co., Ltd., et al. v. Seagate Technology LLC, et al.",
            "NHK Spring v. Seagate Technology",
        ),
        ("Christopher Veto v. The Boeing Company", "Veto v. Boeing"),
        # Initials alone keep their corporate form, which says they are a company.
        ("F.E.B. Corp. v. United States", "F.E.B. Corp. v. United States"),
        # An alias (`fka`, `aka`) reads the party as an organisation and keeps its
        # whole name — right for Prutehi Guahan, never wrong for a person.
        (
            "Department of the Air Force, et al. v. Prutehi Guahan, fka Prutehi Litekyan",
            "Department of the Air Force v. Prutehi Guahan",
        ),
        (
            "Erik Charles Maund, aka Erik Moore v. United States",
            "Erik Charles Maund v. United States",
        ),
        # Three full words may end in a two-word surname, so the name stands whole;
        # with an initial in it, or two words, the surname is the last word.
        (
            "Rio Grande Foundation v. Maggie Toulouse Oliver, in Her Official Capacity as "
            + "Secretary of State of New Mexico",
            "Rio Grande Foundation v. Maggie Toulouse Oliver",
        ),
        ("Stephen Joseph Johnson v. Montana", "Stephen Joseph Johnson v. Montana"),
        ("Kenneth J. Jouppi v. Alaska", "Jouppi v. Alaska"),
        ("Francis Nielsen v. Kekai Watanabe", "Nielsen v. Watanabe"),
        (
            "Suncor Energy (U.S.A.) Inc., et al. v. County Commissioners of Boulder County, "
            + "et al.",
            "Suncor Energy v. County Commissioners of Boulder County",
        ),
        # A corporate-form segment is what makes a person-shaped name a business.
        ("Wealthy, Inc., et al. v. Spencer Cornelia, et al.", "Wealthy v. Cornelia"),
        ("Robinhood Markets, Inc., et al. v. Vinod Sodha, et al.", "Robinhood Markets v. Sodha"),
        # So does a `dba` alias.
        ("Michael Salazar v. Paramount Global, dba 247Sports", "Salazar v. Paramount Global"),
        # Established agency acronyms, and the federal courts named with their seat.
        (
            "Federal Trade Commission, et al. v. National Horsemen's Benevolent and Protective "
            + "Association, et al.",
            "FTC v. National Horsemen's Benevolent and Protective Association",
        ),
        (
            "PG Publishing Company, Inc., dba Pittsburgh Post-Gazette v. National Labor "
            + "Relations Board, et al.",
            "PG Publishing v. NLRB",
        ),
        (
            "U.S. Doge Service, et al. v. United States District Court for the District of "
            + "Columbia, et al.",
            "U.S. Doge Service v. United States District Court",
        ),
        # Institutions keep their name, minus a leading `The` and the place after the comma.
        (
            "Cutberto Viramontes, et al. v. Cook County, Illinois, et al.",
            "Viramontes v. Cook County",
        ),
        (
            "The GEO Group, Inc., a Florida Corporation v. Ugochukwu Nwauzor, et al.",
            "GEO Group v. Nwauzor",
        ),
        (
            "Department of Labor, et al. v. Sun Valley Orchards, LLC",
            "Department of Labor v. Sun Valley Orchards",
        ),
        # A name that is not person-shaped is an organisation, not a surname.
        (
            "Republican National Committee v. Mi Familia Vota, et al.",
            "Republican National Committee v. Mi Familia Vota",
        ),
        ("Arizona, et al. v. Promise Arizona, et al.", "Arizona v. Promise Arizona"),
        (
            "Colorado Bondshares, et al. v. Marin Metropolitan District, et al.",
            "Colorado Bondshares v. Marin Metropolitan District",
        ),
        (
            "Fairfield Sentry Ltd., et al. v. Citibank NA London, et al.",
            "Fairfield Sentry v. Citibank NA London",
        ),
        ("Sara Boysen, et al. v. PeaceHealth, et al.", "Boysen v. PeaceHealth"),
        # A state that is also a given name still starts a person.
        ("Virginia Duncan, et al. v. Rob Bonta, Attorney General of California", "Duncan v. Bonta"),
        # Initials-only names stand whole; `St.` joins the surname.
        (
            "N. R., et al. v. Keith M. Ellison, Attorney General of Minnesota, et al.",
            "N. R. v. Ellison",
        ),
        (
            "D. A., a Minor, By and Through his Mother, B. A., et al. v. Tri County Area "
            + "Schools, et al.",
            "D. A. v. Tri County Area Schools",
        ),
        ("Michael St. Clair v. Christe Quick, Warden", "St. Clair v. Quick"),
        (
            "Ryan O'Donnell, et al. v. City of Chicago, Illinois, et al.",
            "O'Donnell v. City of Chicago",
        ),
        ("Rene Acosta-Tapia v. Todd Blanche, Attorney General", "Acosta-Tapia v. Blanche"),
        # `In re` has one side.
        ("In Re Richard Devillier, et al.", "In re Devillier"),
        ("In Re Joan Farr", "In re Farr"),
        # A line break inside a stored caption is whitespace.
        (
            "Alvin B. White, Individually and as Trustee for the White Revocable Living \n"
            + "Trust dated January 6, 2010 v. U.S. Bank National Association, as Legal "
            + "Title Trustee for Truman 2016 SC6 Title Trust",
            "White v. U.S. Bank National Association",
        ),
    ],
)
def test_the_short_caption_of_a_committed_caption(caption: str, expected: str) -> None:
    assert short_caption(caption) == expected


@pytest.mark.parametrize(
    "caption",
    [
        # The conventional short form is an acronym no rule derives from the words
        # ("RAICES"), so the organisation is too long to shorten and the whole is null.
        "Markwayne Mullin, Secretary of Homeland Security, et al. v. Refugee and Immigrant "
        + "Center for Education and Legal Services, et al.",
        "National Park Service, et al. v. National Trust for Historic Preservation in the "
        + "United States",
        "Thomas Crowther, et al. v. Board of Regents of the University System of Georgia, "
        + "et al.",
        # A surname particle: where the surname starts is not in the caption.
        "Philip L. Rhoney, Acting Director of the Buffalo Field Office of U.S. Immigration "
        + "and Customs Enforcement v. Ricardo Aparecido Barbosa da Cunha",
        # Four words may end in a two-word surname.
        "Kevin Isaac Montoya Palacios v. Vernon Liggins, Acting Field Office Director, "
        + "Baltimore Field Office, United States Immigration and Customs Enforcement, et al.",
        "Katherine L. Hobbins Forester, et al. v. Adam Gerol, et al.",
        # No ` v. `, or more than one.
        "Ex parte Someone",
        "A v. B v. C",
        "",
    ],
)
def test_the_rule_declines_what_it_cannot_shorten_with_confidence(caption: str) -> None:
    assert short_caption(caption) is None


def test_no_caption_has_no_short_form() -> None:
    assert short_caption(None) is None
