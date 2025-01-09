import sys
from lib import read_account, read_members, eprint, formatprice, do_or_exit

def transform_description(account_row, members):
    """
    Transform the description field of an account row.
    - if the row is 넬비, the result is either '<이름> 회비' or '<이름> 넬방사용료'
    - otherwise, the result is the same as row["memo"]
    """

    넬비세부이름 = {
        "정회원": "회비",
        "OB": "넬방사용료",
    }

    if account_row["memo"] == "넬비":
        assert account_row["type"] == "입금"

        # find member
        member_candidates = [m for m in members if m["name"] in account_row["description"]]
        if len(member_candidates) != 1:
            eprint(f"Warning: Multiple or no member found for '{account_row['description']}'. Ignoring 넬비...")
            return account_row["memo"]
        member = member_candidates[0]

        # determine description according to member grade
        if member["grade"] in 넬비세부이름:
            assert ' ' not in member["name"]
            if account_row["amount"] != 20000:
                eprint(f"Warning: Unexpected amount '{account_row['amount']}' for {member['name']} 넬비")
            return member["name"] + " " + 넬비세부이름[member["grade"]]
        else:
            eprint(f"Warning: Unexpected member grade '{member['grade']}'. Ignoring 넬비...")
            return account_row["memo"]
    else:
        # check for hard-coded keywords
        keywords = list(넬비세부이름.values())
        for keyword in keywords:
            if keyword in account_row["memo"]:
                eprint(f"Warning: '{account_row['memo']}' is hard-coded in raw 메모.")

        return account_row["memo"]

def main():
    # parse arguments
    if len(sys.argv) != 2:
        print("Usage: python process.py <input>")
        sys.exit(1)

    input_filename = sys.argv[1]

    # read data
    account: list[dict] = do_or_exit(read_account, input_filename, task_label="reading account data")
    members: list[dict] = do_or_exit(read_members, "members.csv", task_label="reading members data")

    # print markdown table & collect 넬비낸 members
    회비낸 = []
    넬방사용료낸 = []
    print("|날짜|구분|내용|금액(수입)|금액(지출)|잔액|")
    print("|----|----|----|----------|----------|----|")
    for row in account:
        date = row["date"]
        if row["type"] == "입금":
            assert row["amount"] > 0
            type = "수입"
            income = formatprice(row["amount"])
            outcome = ""
        else:
            assert row["type"] == "출금"
            assert row["amount"] < 0
            type = "지출"
            income = ""
            outcome = formatprice(-row["amount"])
        balance = formatprice(row["balance"])
        description = transform_description(row, members)

        if description.endswith(" 회비"):
            회비낸.append(description.split(" ")[0])
        elif description.endswith(" 넬방사용료"):
            넬방사용료낸.append(description.split(" ")[0])

        print(f"|{date}|{type}|{description}|{income}|{outcome}|{balance}|")

    # print 넬비낸 members
    정회원 = [m for m in members if m["grade"] == "정회원"]
    회비안낸 = [m["name"] for m in 정회원 if m["name"] not in 회비낸]
    print(f"\n- 회비 낸 사람({len(회비낸)}/{len(정회원)}): {', '.join(sorted(회비낸))}")
    print(f"  - 안 낸 사람({len(회비안낸)}): {', '.join(sorted(회비안낸))}")
    print(f"- 넬방사용료 낸 사람({len(넬방사용료낸)}/-): {', '.join(sorted(넬방사용료낸))}")

if __name__ == "__main__":
    main()
