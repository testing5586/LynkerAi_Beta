def calculate_match_score(user1, user2):
    score = 0
    matching_items = []

    if user1['ziwei_palace'] == user2['ziwei_palace']:
        matching_items.append('ziwei_palace')
    if user1['main_star'] == user2['main_star']:
        matching_items.append('main_star')
    if user1['shen_palace'] == user2['shen_palace']:
        matching_items.append('shen_palace')

    if len(matching_items) == 3:
        score = 100
    elif len(matching_items) == 2:
        score = 70
    elif len(matching_items) == 1:
        score = 40
    else:
        score = 0

    return score, matching_items


def print_match_report(user1, user2):
    score, matching_items = calculate_match_score(user1, user2)
    print(f"Match Score: {score}")
    if matching_items:
        print(f"Matching Items: {', '.join(matching_items)}")
    else:
        print("No matching items.")


# Example usage:
user1 = {
    'ziwei_palace': 'A',
    'main_star': 'B',
    'shen_palace': 'C'
}

user2 = {
    'ziwei_palace': 'A',
    'main_star': 'D',
    'shen_palace': 'C'
}

print_match_report(user1, user2)