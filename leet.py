def naive(s: str) -> int:
    if not s:
        return 0

    def _fn(index: int):
        hs = set()
        c = 0
        for i in range(index, len(s)):
            char = s[i]
            if char in hs:
                return c
            c += 1
            hs.add(char)
        return c

    return max(_fn(i) for i in range(len(s)))


def sliding(s: str) -> int:
    if not s:
        return 0
    j, m = 0, 0
    hs = set()
    for i in range(len(s)):
        c = s[i]
        while c in hs:
            hs.remove(s[j])
            j += 1
        hs.add(c)
        m = max(m, i - j + 1)

    return m


suite = [
    "abcabcbb",  # 3
    "bbbbb",  # 1
    "pwwkew",  # 3
    "dvdf",  # 3
    "",  # 0
]

# print("NAIVE SOLUTION")
# for test in suite:
#     print(naive(test))
# print()

# print("OPTIMAL SOLUTION WITH SLIDING WINDOW")
# for test in suite:
#     print(sliding(test))

min_size = 3


# def numby(nums: list[int]) -> int:
#     if len(nums) < min_size:
#         return 0

#     right = 1
#     count = 0

#     for left in range(len(nums)):
#         if left > len(nums) - 2:
#             break

#         # print(left)
#         diff_desired = nums[left + 1] - nums[left]
#         diff_actual = nums[left] - nums[left]
#         while diff_actual != diff_desired:

#         # while nums[right] - nums[left] != diff:
#         #     print(1)

#     return count


# numby([1, 3, 5, 7, 9])


def sliding_window_example(nums: list[int], k: int) -> int:
    left, right, max_sum = 0, 2, 0

    for left in range(len(nums)):
        curr_sum = sum([nums[left]])


print(sliding_window_example([1, 2, 6, 2, 4, 1], 3))
