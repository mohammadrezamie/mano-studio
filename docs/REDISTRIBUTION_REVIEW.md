# Redistribution review — open, not approved

The frozen candidate includes Qt/PySide components under the LGPLv3/GPLv3/Commercial alternatives. The package METADATA explicitly identifies the LGPL-3.0-only option, and the standard LGPLv3 text is included in third-party notices. The automated preflight verifies both facts and records a separate corresponding-source/relink review flag; it does not treat the presence of license text as permission to distribute.

Source evidence collected from official Qt endpoints:
- PySide/Shiboken 6.12.0 source archive: vendor SHA-256 verified, 099c1a597cf33c1b000e11cf68a0b82d216fb802bf81726efc720394f10c7751.
- QtBase 6.12.0 source archive: vendor SHA-256 verified, a951bd163c7b80fc6b8c88d7668fb56abf91c152373e13c10666763238131307.
- QtSvg 6.12.0 source archive: vendor SHA-256 verified, e4ab39534ec97987b1b9b60ef7f4d3253d5912a69f8c713a01753174a4029331.

The final runtime build removes the unused Qt QML/Quick group and the unused Qt PDF pair. It must be verified from the replacement archives that neither runtime group remains. The failed QtWebEngine source lookup was a 404 because Qt PDF/WebEngine are separately distributed extensions in Qt 6.12; the final candidate removes Qt PDF, so it is not a runtime source obligation.

Still required before public distribution:
1. Map each shipped Qt/PySide binary to its exact source revision and build configuration, including any vendor patches.
2. Publish or bundle complete corresponding source for shipped LGPL libraries and their required third-party sources, with checksums and build instructions.
3. Document how users replace/relink the dynamically loaded Qt libraries and run their modified versions; verify the installed layout permits this.
4. Complete third-party notice and license review for the actual shipped modules, not all files in the source archive.
5. Obtain independent legal review of the LGPL/GPL route and final installer/portable contents.

The release gate remains manual-review-required and public_release_approved=false. Do not publish solely because CI passes.
