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
- 일단 lib.py의 Trie Class부터 구현하기
- main 구현하기

힌트: 한 글자짜리 자료에도 그냥 str을 쓰기에는 메모리가 아깝다...
"""


def main() -> None:
    MOD = 1_000_000_007
    input = sys.stdin.readline
    n_line = input().strip()
    if not n_line:
        return
    n = int(n_line)

    trie: Trie = Trie()
    for _ in range(n):
        name = input().strip()
        trie.push([ord(c) for c in name])

    max_k = 0
    for node in trie:
        k = len(node.children) + (1 if node.is_end else 0)
        if k > max_k:
            max_k = k

    fact = [1] * (max_k + 1)
    for x in range(2, max_k + 1):
        fact[x] = (fact[x - 1] * x) % MOD

    ans = 1
    for node in trie:
        k = len(node.children) + (1 if node.is_end else 0)
        ans = (ans * fact[k]) % MOD

    print(ans)


if __name__ == "__main__":
    main()