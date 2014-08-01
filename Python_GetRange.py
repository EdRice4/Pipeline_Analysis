# def get_range(range_file, start, end):
#     operators = ['in', '==']
#     start = 0
#     end = 0
#     for num, line in enumerate(range_file, start=1):
#         if start == line.lower():
#             start = num
#         if end == line.lower():
#             end = num
#     return start, end

def get_range(range_file, start, end):
        range_start = 0
        range_end = 0
        for num, line in enumerate(range_file, start=1):
            if start == line.lower():
                range_start = num
            if end == line.lower():
                range_end = num
        return range_start, range_end

with open('Cerapachys_ULTIMATE_NOTRM_UNDERSCORE.nex', 'r') as seq_file:
    print get_range(seq_file, '\tmatrix\n', '\n')