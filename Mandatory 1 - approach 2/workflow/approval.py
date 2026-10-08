def request_approval(changes):
    print("\n===== PROPOSED CODE CHANGES =====\n")

    for change in changes:
        print(f"FILE: {change['path']}")
        print("-" * 60)
        print(change["content"])
        print("-" * 60)
        print()

    answer = input("Apply these changes? [y/N]: ")

    return answer.strip().lower() == "y"