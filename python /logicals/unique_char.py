a = "string"


def unique_string(a):
    unique = True
    for index, letter in enumerate(a):
        for index, let in enumerate(a[index+1:]):
            if let == letter:
                unique = False
                return unique

    return unique


res = unique_string(a)

print(res)



def replace_spaces(string):
    while ' ' == string[0]:
        string = string.replace(' ', '', 1)

    return string

b = "test try to    "
rev = replace_spaces(b)
rev = replace_spaces(rev[::-1])



res = rev[::-1].replace(" ", "%20")
print(res)

