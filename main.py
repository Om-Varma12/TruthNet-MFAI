from pprint import pprint

from pipeline.run_pipeline import run


def main():
    title = input("Enter news title: ").strip()
    domain = input("Enter source domain/url: ").strip()
    tweets = int(input("Enter tweet count: ").strip())

    result = run(title=title, domain_url=domain, tweet_count=tweets)
    pprint(result)


if __name__ == "__main__":
    main()
