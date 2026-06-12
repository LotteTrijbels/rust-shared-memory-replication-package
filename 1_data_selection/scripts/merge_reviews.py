# put everything in one file
import json
import glob

def main():
    all_reviews = []

    for path in glob.glob("repos/*/*/shared_memory_review.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        all_reviews.append({
            "path": path,
            **data
        })

    with open("all-shared-memory.json", "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, indent=2)


if __name__ == "__main__":
    main()