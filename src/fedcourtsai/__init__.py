"""fedcourtsai: agentic system to predict events in US federal courts."""

# Import casestore for its side effect: it registers the corpus dual-write sink
# (corpus does not import casestore, to avoid an import cycle — see corpus.MirrorSink).
# The sink is gated on FEDCOURTS_CASESTORE_URL, so this is inert unless enabled.
from . import casestore as casestore

__version__ = "0.0.1"
