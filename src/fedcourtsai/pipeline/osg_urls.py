"""Whether a URL is on the Office of the Solicitor General's section of www.justice.gov.

A leaf, like :mod:`.paper_only`, so the readers that must tell a stored row the
Solicitor General's posted copy (the QP extract, the case-summary stage check)
ask it without importing the fetcher (:mod:`.sg_briefs`).
"""

from __future__ import annotations

from urllib.parse import unquote, urlsplit

#: The host the Office of the Solicitor General's pages are served from.
OSG_HOST = "www.justice.gov"
#: The path prefix of the Office's own section.
OSG_PATH_PREFIX = "/osg/"


def is_osg_url(url: str) -> bool:
    """Whether ``url`` is HTTPS on the Office's section of ``www.justice.gov``.

    The same posture as :func:`fedcourtsai.supremecourt.is_court_url`: a link
    out of a listing row is upstream text and what it returns is stored as a
    filed document, so the scheme, the exact host, the default port and the
    path prefix are all checked, userinfo is refused, and so is any character
    that is not printable (``urlsplit`` drops tabs and newlines before parsing).
    """
    if any(not char.isprintable() for char in url):
        return False
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        return False
    if parts.scheme != "https" or (parts.hostname or "").lower() != OSG_HOST:
        return False
    if parts.username or parts.password or port not in (None, 443):
        return False
    # A dot segment would be resolved by the client after this check, so
    # "/osg/../x" would reach a path outside the section; one is refused in
    # any spelling, percent-encoded included.
    segments = unquote(parts.path).split("/")
    if any(segment in (".", "..") for segment in segments):
        return False
    return parts.path.startswith(OSG_PATH_PREFIX)
