import subfish

def main()-> None:
    print("Subfish REPL v0.1.0")
    subf = subfish.Subfish()
    while 1:
        cmd = input(">> ")
        cmd = subfish.preprocess(cmd)
        for ch in cmd:
            subf.feed(ch)

if __name__ == "__main__":
    main()
