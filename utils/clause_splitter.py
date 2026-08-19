import re


class ClauseSplitter:

    def split(self, document: dict) -> list[dict]:
        """
        Generic structural clause splitter.

        Strong signals:
        - DOCX heading styles
        - numbered provisions
        - lettered provisions
        - roman numeral provisions
        - bracketed substantive provisions

        It does not depend on legal clause names.
        """

        blocks = document.get("blocks", [])

        if not blocks:
            return []

        clauses = []
        current = None

        for block in blocks:

            text = block["text"].strip()

            if not text:
                continue

            if self._is_clause_start(text, block):

                if current:
                    self._save_clause(
                        clauses,
                        current,
                    )

                current = {
                    "title": self._extract_title(text),
                    "text": text,
                    "source_blocks": [block],
                }

            else:

                if current is None:

                    current = {
                        "title": "Preamble",
                        "text": text,
                        "source_blocks": [block],
                    }

                else:

                    current["text"] += " " + text
                    current["source_blocks"].append(block)

        if current:
            self._save_clause(
                clauses,
                current,
            )

        return clauses

    # ---------------------------------------------------------
    # Clause start
    # ---------------------------------------------------------

    def _is_clause_start(
        self,
        text: str,
        block: dict,
    ) -> bool:

        block_type = block.get("type", "")

        # Explicit DOCX heading
        if block_type == "heading":
            return True

        # Numbered provision
        if self._is_numbered(text):
            return True

        # Lettered provision
        if self._is_lettered(text):
            return True

        # Roman numeral provision
        if self._is_roman(text):
            return True

        # Bracketed substantive provision
        if self._is_bracketed_provision(text):
            return True

        return False

    # ---------------------------------------------------------
    # Numbered provisions
    # ---------------------------------------------------------

    def _is_numbered(self, text: str) -> bool:

        pattern = (
            r"^(?:section\s+)?"
            r"\d+(?:\.\d+)*"
            r"(?:[\.\):\-])"
            r"(?:\s+|$)"
        )

        return bool(
            re.match(
                pattern,
                text,
                re.IGNORECASE,
            )
        )

    # ---------------------------------------------------------
    # Lettered provisions
    # ---------------------------------------------------------

    def _is_lettered(self, text: str) -> bool:

        pattern = (
            r"^(?:"
            r"\([a-zA-Z]\)"
            r"|"
            r"[a-zA-Z]\."
            r")\s+"
        )

        return bool(
            re.match(pattern, text)
        )

    # ---------------------------------------------------------
    # Roman numeral provisions
    # ---------------------------------------------------------

    def _is_roman(self, text: str) -> bool:

        pattern = (
            r"^\("
            r"(?:"
            r"i{1,3}"
            r"|iv"
            r"|v"
            r"|vi{0,3}"
            r"|ix"
            r"|x"
            r")"
            r"\)\s+"
        )

        return bool(
            re.match(
                pattern,
                text,
                re.IGNORECASE,
            )
        )

    # ---------------------------------------------------------
    # Bracketed provisions
    # ---------------------------------------------------------

    def _is_bracketed_provision(
        self,
        text: str,
    ) -> bool:

        if not text.startswith("["):
            return False

        if len(text) < 40:
            return False

        # If the entire thing is something like
        # [INVESTOR] [COMPANY], don't classify it.
        if text.upper() in {
            "[INVESTOR] [COMPANY]",
            "[SIGNATURE PAGE FOLLOWS]",
            "[PORTFOLIO COMPANY LETTERHEAD]",
        }:
            return False

        return True

    # ---------------------------------------------------------
    # Title
    # ---------------------------------------------------------

    def _extract_title(self, text: str) -> str:

        match = re.match(
            r"^(?:section\s+)?"
            r"(\d+(?:\.\d+)*)",
            text,
            re.IGNORECASE,
        )

        if match:
            return f"Provision {match.group(1)}"

        match = re.match(
            r"^(\([a-zA-Z]\)|[a-zA-Z]\.)",
            text,
        )

        if match:
            return f"Provision {match.group(1)}"

        match = re.match(
            r"^(\([ivxlcdm]+\))",
            text,
            re.IGNORECASE,
        )

        if match:
            return f"Provision {match.group(1)}"

        return "Provision"

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    def _save_clause(
        self,
        clauses: list,
        clause: dict,
    ):

        text = clause["text"].strip()

        if len(text) < 40:
            return

        clauses.append({
            "title": clause["title"],
            "text": text,
            "source_blocks": clause["source_blocks"],
        })