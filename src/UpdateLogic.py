import enum


class Result(enum.Enum):
    NO_MSGBOX = 0
    NO_UPDATE_FOUND = 1
    FOUND_BETA = 2
    FOUND_FULL = 3
    FOUND_DOWNGRADE = 4

    RATE_LIMIT_EXCEEDED = 5
    NO_CONNECTION = 6


class Report:
    def __init__(self, value: int | Result, is_terminal: bool):
        self.is_terminal: bool = is_terminal
        self.value: Result | int = value


class auto:
    def __init__(self, amount_nodes):
        self.nodes: list[node] = [None] * amount_nodes

    def create_nodes(self):
        raise RuntimeError("Not implemented")

    def test(self, *inputs: bool) -> Result:
        if None in self.nodes:
            self.create_nodes()
            if None in self.nodes:
                raise RuntimeError("Incorrect implementation of createnodes")
        if len(inputs) != len(self.nodes):
            raise ValueError("Input length does not match node length.")
        for i, x in enumerate(inputs):
            self.nodes[i].set(x)
        current_idx: int = 0
        while True:
            res: Report = self.nodes[current_idx].step()
            if res.is_terminal:
                return res.value
            current_idx = res.value


class node:
    def __init__(self, true_index: Report, false_index: Report):
        self.value = False
        self.true_index: Report = true_index
        self.false_index: Report = false_index

    def step(self) -> Report:
        if self.value == True:
            return self.true_index
        return self.false_index

    def set(self, value: bool):
        self.value = value


class Logic(auto):
    def __init__(self):
        super().__init__(8)

    def create_nodes(self):
        self.nodes[0] = node(Report(1, False), Report(2, False))
        self.nodes[1] = node(Report(6, False), Report(3, False))
        self.nodes[2] = node(Report(4, False), Report(5, False))
        self.nodes[3] = node(
            Report(Result.FOUND_BETA, True), Report(Result.FOUND_FULL, True)
        )
        self.nodes[4] = node(Report(7, False), Report(Result.NO_MSGBOX, True))
        self.nodes[5] = node(Report(Result.FOUND_FULL, True), Report(6, False))
        self.nodes[6] = node(
            Report(Result.NO_UPDATE_FOUND, True), Report(Result.NO_MSGBOX, True)
        )
        self.nodes[7] = node(
            Report(Result.FOUND_FULL, True), Report(Result.FOUND_DOWNGRADE, True)
        )

    def test(
        self,
        is_beta_enabled: bool,
        current_version_is_beta: bool,
        current_version_is_latest: bool,
        latest_is_beta: bool,
        call_origin_menu: bool,
        call_origin_search: bool,
        exists_full_version_above_current_beta: bool,
        exists_newer_version: bool,
    ) -> Result:
        return super().test(
            is_beta_enabled,
            current_version_is_latest,
            current_version_is_beta,
            latest_is_beta,
            call_origin_menu,
            exists_newer_version,
            call_origin_search,
            exists_full_version_above_current_beta,
        )
