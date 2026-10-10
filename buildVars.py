from site_scons.site_tools.NVDATool.typings import (
    AddonInfo,
    BrailleTables,
    SymbolDictionaries,
)
from site_scons.site_tools.NVDATool.utils import _

addon_info = AddonInfo(
    addon_name="instantTimer",
    addon_summary=_("Instant Timer"),
    addon_description=_(
        """Countdown timers and stopwatch for NVDA with 5 preset timers, an ad-hoc quick timer, a modal command layer, and audio and speech alerts."""
    ),
    addon_version="2026.2",
    addon_changelog=_(
        """- Version 2026.2: The command layer now opens with NVDA+Y to avoid a conflict with Instant Access. Renaming a running timer no longer stops it. The report-all command includes the stopwatch. Settings are saved safely and active timers survive an NVDA crash. Fixed the layer staying active after an error, and other small fixes."""
    ),
    addon_author="Kamal Yaser <kamalyaser31@gmail.com>",
    addon_url="https://github.com/kamalyaser31/instantTimer",
    addon_sourceURL="https://github.com/kamalyaser31/instantTimer",
    addon_docFileName="readme.html",
    addon_minimumNVDAVersion="2024.1.0",
    addon_lastTestedNVDAVersion="2026.2.0",
    addon_updateChannel=None,
    addon_license="GPL v2",
    addon_licenseURL="https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
)

pythonSources = ["addon/**/*.py"]
i18nSources: list[str] = pythonSources + ["buildVars.py"]
excludedFiles: list[str] = []
baseLanguage: str = "en"
markdownExtensions: list[str] = []
brailleTables: BrailleTables = {}
symbolDictionaries: SymbolDictionaries = {}
speechDictionaries: dict = {}
