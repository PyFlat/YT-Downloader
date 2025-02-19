import enum


class result(enum.Enum):
    NO_MSGBOX = 0
    NO_UPDATE_FOUND = 1
    FOUND_BETA = 2
    FOUND_FULL = 3
    FOUND_DOWNGRADE = 4


class report:
    def __init__(self, value: int | result, is_terminal: bool):
        self.is_terminal: bool = is_terminal
        self.value: result | int = value


class auto:
    def __init__(self, amount_nodes):
        self.nodes: list[node] = [None] * amount_nodes

    def create_nodes(self):
        raise RuntimeError("Not implemented")

    def test(self, *inputs: bool) -> result:
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
            res: report = self.nodes[current_idx].step()
            if res.is_terminal:
                return res.value
            current_idx = res.value


class node:
    def __init__(self, true_index: report, false_index: report):
        self.value = False
        self.true_index: report = true_index
        self.false_index: report = false_index

    def step(self) -> report:
        if self.value == True:
            return self.true_index
        return self.false_index

    def set(self, value: bool):
        self.value = value


class logic(auto):
    def __init__(self):
        super().__init__(8)

    def create_nodes(self):
        self.nodes[0] = node(report(1, False), report(2, False))
        self.nodes[1] = node(report(6, False), report(3, False))
        self.nodes[2] = node(report(4, False), report(5, False))
        self.nodes[3] = node(
            report(result.FOUND_BETA, True), report(result.FOUND_FULL, True)
        )
        self.nodes[4] = node(report(7, False), report(result.NO_MSGBOX, True))
        self.nodes[5] = node(report(result.FOUND_FULL, True), report(6, False))
        self.nodes[6] = node(
            report(result.NO_UPDATE_FOUND, True), report(result.NO_MSGBOX, True)
        )
        self.nodes[7] = node(
            report(result.FOUND_FULL, True), report(result.FOUND_DOWNGRADE, True)
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
    ) -> result:
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
