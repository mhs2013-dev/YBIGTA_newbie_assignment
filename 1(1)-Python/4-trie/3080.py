from lib import Trie
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