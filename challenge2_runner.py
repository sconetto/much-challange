from subprocess import call


def main():
    """Main function to execute the runner process"""
    # Creates backup files
    call(["touch", "/tmp/last.bkp"])
    call(["touch", "/tmp/objects.bkp"])

    # Initialize the backup files
    call("echo 0 > /tmp/last.bkp", shell=True)
    call("echo '[]' > /tmp/objects.bkp", shell=True)

    # While don't recieve signal 1 (terminated execution [check challenge2.py])
    # call challenge2.py to execute
    while not call(["python3", "challenge2.py"]):
        continue

    return True


if __name__ == "__main__":
    main()
