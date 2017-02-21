from models import MemberModel


def main():
    for member in MemberModel.scan(limit=100):
        print member.username


if __name__ == "__main__":
    main()
