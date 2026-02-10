class RulesHelperService:

    @staticmethod
    def get_docs_gost_design_rules():
        with open("data/docs/GOST_DESIGN_RULES.md", "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def get_charlie_tools_guide():
        with open("docs/data/CHARLIE_TOOLS.md", "r", encoding="utf-8") as f:
            return f.read()