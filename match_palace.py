def calculate_match_score(userA, userB):
    matching_fields = []
    score = 0

    if userA['ziwei_palace'] == userB['ziwei_palace']:
        matching_fields.append('ziwei_palace')
    if userA['main_star'] == userB['main_star']:
        matching_fields.append('main_star')
    if userA['shen_palace'] == userB['shen_palace']:
        matching_fields.append('shen_palace')

    matches = len(matching_fields)
    if matches == 3:
        score = 100
    elif matches == 2:
        score = 70
    elif matches == 1:
        score = 40
    else:
        score = 0

    print(f"Match Score: {score}")
    if matching_fields:
        print(f"Matching Fields: {', '.join(matching_fields)}")
    else:
        print("No Matching Fields.")
    return score, matching_fields


# ✅ 为兼容旧代码
match_palace = calculate_match_score

if __name__ == "__main__":
    user1 = {"ziwei_palace": "巳", "main_star": "天府", "shen_palace": "巳"}
    user2 = {"ziwei_palace": "午", "main_star": "武曲", "shen_palace": "巳"}
    calculate_match_score(user1, user2)
