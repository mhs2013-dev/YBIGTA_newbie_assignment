from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Iterable


"""
TODO:
- Trie.push 구현하기
- (필요할 경우) Trie에 추가 method 구현하기
"""


T = TypeVar("T")


@dataclass
class TrieNode(Generic[T]):
    body: Optional[T] = None
    children: list[int] = field(default_factory=lambda: [])
    is_end: bool = False


class Trie(list[TrieNode[T]]):
    def __init__(self) -> None:
        super().__init__()
        self.append(TrieNode(body=None))

    def push(self, seq: Iterable[T]) -> None:
        """
        seq: T의 열 (list[int]일 수도 있고 str일 수도 있고 등등...)

        action: trie에 seq을 저장하기
        """
        # 구현하세요!
        pointer = 0
        for token in seq:
            nxt = self._find_child(pointer, token)
            if nxt is None:
                nxt = len(self)
                self.append(TrieNode(body=token))
                self[pointer].children.append(nxt)
            pointer = nxt
        self[pointer].is_end = True

    # 구현하세요!
    def _find_child(self, node_idx: int, token: T) -> Optional[int]:
        """node_idx의 자식 중 body==token 인 노드 인덱스를 찾습니다. 없으면 None."""
        for child_idx in self[node_idx].children:
            if self[child_idx].body == token:
                return child_idx
        return None


import sys


"""
TODO:
- 일단 Trie부터 구현하기
- count 구현하기
- main 구현하기
"""


def count(trie: Trie, query_seq: str) -> int:
    """
    trie - 이름 그대로 trie
    query_seq - 단어 ("hello", "goodbye", "structures" 등)

    returns: query_seq의 단어를 입력하기 위해 버튼을 눌러야 하는 횟수
    """
    pointer = 0
    cnt = 0

    for element in query_seq:
        if len(trie[pointer].children) > 1 or trie[pointer].is_end:
            cnt += 1

        new_index = None # 구현하세요!
        token = ord(element)
        for child_idx in trie[pointer].children:
            if trie[child_idx].body == token:
                new_index = child_idx
                break

        assert new_index is not None

        pointer = new_index

    return cnt + int(len(trie[0].children) == 1)


def main() -> None:
    data = sys.stdin.buffer.read().split()
    i = 0
    out_lines: list[str] = []

    while i < len(data):
        n = int(data[i])
        i += 1

        words = [data[i + k].decode() for k in range(n)]
        i += n

        trie: Trie = Trie()
        for w in words:
            trie.push([ord(c) for c in w])

        total = 0
        for w in words:
            total += count(trie, w)

        out_lines.append(f"{total / n:.2f}")

    sys.stdout.write("\n".join(out_lines))


if __name__ == "__main__":
    main()