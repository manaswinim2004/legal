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

        if block_type in ("heading", "title"):
            return True

        if self._is_numbered(text):
            return True

        if self._is_lettered(text):
            return True

        if self._is_roman(text):
            return True

        if self._is_all_caps_heading(text):
            return True

        if self._is_bracketed_provision(text):
            return True

        return False

    def _is_numbered(self, text: str) -> bool:
        pattern = (
            r"^(?:(?:section|article|clause|paragraph|item)\s+)?"
            r"\d+(?:\.\d+)*"
            r"(?:[\.\):\-\s]|$)"
        )
        return bool(re.match(pattern, text, re.IGNORECASE))

    def _is_all_caps_heading(self, text: str) -> bool:
        # Match standalone all-caps headings like "CONFIDENTIAL INFORMATION", "TERM AND TERMINATION"
        cleaned = text.strip().rstrip(".:-")
        words = cleaned.split()
        if 1 <= len(words) <= 8 and len(cleaned) <= 60:
            if cleaned.isupper() and any(c.isalpha() for c in cleaned):
                return True
        return False

    def _is_lettered(self, text: str) -> bool:
        pattern = r"^(?:\([a-zA-Z]\)|[a-zA-Z]\.)\s+"
        return bool(re.match(pattern, text))

    def _is_roman(self, text: str) -> bool:
        pattern = r"^(?:\((?:i{1,3}|iv|v|vi{0,3}|ix|x)\)|(?:i{1,3}|iv|v|vi{0,3}|ix|x)\.)(?:\s+|$)"
        return bool(re.match(pattern, text, re.IGNORECASE))

    def _is_bracketed_provision(
        self,
        text: str,
    ) -> bool:
        if not text.startswith("["):
            return False

        if len(text) < 20:
            return False

        if text.upper() in {
            "[INVESTOR] [COMPANY]",
            "[SIGNATURE PAGE FOLLOWS]",
            "[PORTFOLIO COMPANY LETTERHEAD]",
        }:
            return False

        return True

    def _extract_title(self, text: str) -> str:
        # Try Article/Section/Clause
        match = re.match(
            r"^((?:section|article|clause|paragraph)\s+\d+(?:\.\d+)*)",
            text,
            re.IGNORECASE,
        )
        if match:
            return match.group(1).title()

        match = re.match(r"^(\d+(?:\.\d+)*)", text)
        if match:
            return f"Section {match.group(1)}"

        match = re.match(r"^(\([a-zA-Z]\)|[a-zA-Z]\.)", text)
        if match:
            return f"Item {match.group(1)}"

        match = re.match(r"^(\((?:i{1,3}|iv|v|vi{0,3}|ix|x)\)|(?:i{1,3}|iv|v|vi{0,3}|ix|x)\.)", text, re.IGNORECASE)
        if match:
            return f"Item {match.group(1)}"

        # If it's an all-caps short heading, use that as title
        cleaned = text.strip().rstrip(".:-")
        if cleaned.isupper() and len(cleaned) <= 60:
            return cleaned.title()

        return "Provision"

    def _save_clause(
        self,
        clauses: list,
        clause: dict,
    ):
        text = clause["text"].strip()
        if len(text) < 15:
            return

        clauses.append({
            "title": clause["title"],
            "text": text,
            "source_blocks": clause["source_blocks"],
        })